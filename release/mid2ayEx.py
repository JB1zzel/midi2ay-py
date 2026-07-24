#!/usr/bin/env python3
"""
midi2ay.py - Convert MIDI to ZX Spectrum AY-3-8912 music ASM
Based on the midi2ay algorithm by Quique Llaría
Requires: pip install mido
"""

import sys
import mido

# AY-3-8912 Register Constants
AY_REGS = {
    'TONE_A_FINE': 0,
    'TONE_A_COARSE': 1,
    'TONE_B_FINE': 2,
    'TONE_B_COARSE': 3,
    'TONE_C_FINE': 4,
    'TONE_C_COARSE': 5,
    'NOISE': 6,
    'MIXER': 7,
    'VOL_A': 8,
    'VOL_B': 9,
    'VOL_C': 10
}

CHANNEL_REGS = [
    [AY_REGS['TONE_A_FINE'], AY_REGS['TONE_A_COARSE'], AY_REGS['VOL_A']],
    [AY_REGS['TONE_B_FINE'], AY_REGS['TONE_B_COARSE'], AY_REGS['VOL_B']],
    [AY_REGS['TONE_C_FINE'], AY_REGS['TONE_C_COARSE'], AY_REGS['VOL_C']],
]

AY_CLOCK = 1773400.0
FRAMES_PER_SECOND = 50
MAX_WAIT = 255
NUM_CHANNELS = 3
NUM_MIDI_CHANNELS = 16
MAX_NOTE = 127
MAX_VOLUME = 15


def midi_note_to_period(note):
    """Convert MIDI note number to AY period value."""
    if not 0 <= note <= MAX_NOTE:
        return 0
    
    freq = 440.0 * (2.0 ** ((note - 69) / 12.0))
    period = int(AY_CLOCK / (16.0 * freq) + 0.5)
    return max(1, min(4095, period))


class MidiToAY:
    """Convert MIDI file to AY music data format."""
    
    def __init__(self):
        # MIDI state
        self.notes = [[-1] * (MAX_NOTE + 1) for _ in range(NUM_MIDI_CHANNELS)]
        self.channel_active = [0] * NUM_MIDI_CHANNELS
        
        # AY state
        self.current_state = [[0, 0, 0] for _ in range(NUM_CHANNELS)]
        self.next_state = [[0, 0, 0] for _ in range(NUM_CHANNELS)]
        
        # Output buffer
        self.output = []
        self.pending_wait = 0
        self.last_reg_value = {}
        
        # MIDI timing
        self.tempo = 500000  # microseconds per quarter note
        self.ticks_per_beat = 480
    
    def ticks_to_frames(self, ticks):
        """Convert MIDI ticks to 50Hz frame count."""
        seconds = (ticks / self.ticks_per_beat) * (self.tempo / 1_000_000.0)
        return max(0, int(seconds * FRAMES_PER_SECOND + 0.5))
    
    def write_reg(self, reg, value):
        """Write to AY register with delta compression."""
        if self.last_reg_value.get(reg) == value:
            return
        
        # Flush pending wait in chunks
        delta = self.pending_wait
        while delta > MAX_WAIT:
            self.output.extend([MAX_WAIT, 0xFE, 0x00])
            delta -= MAX_WAIT
        
        self.output.extend([delta, reg, value])
        self.pending_wait = 0
        self.last_reg_value[reg] = value
    
    def flush_wait(self):
        """Flush any remaining wait and append termination sequence."""
        delta = self.pending_wait
        while delta > MAX_WAIT:
            self.output.extend([MAX_WAIT, 0xFE, 0x00])
            delta -= MAX_WAIT
        self.output.extend([delta, 0xFF, 0x00])
    
    def parse_midi_file(self, filename):
        """Parse MIDI file and generate AY data."""
        mid = mido.MidiFile(filename)
        self.ticks_per_beat = mid.ticks_per_beat
        
        # Collect all note events
        events = []
        for track in mid.tracks:
            time = 0
            for msg in track:
                time += msg.time
                if msg.type == 'set_tempo':
                    self.tempo = msg.tempo
                elif msg.type == 'note_on' and msg.velocity > 0:
                    events.append((time, True, msg.channel, msg.note, msg.velocity))
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    events.append((time, False, msg.channel, msg.note, 0))
        
        events.sort(key=lambda x: x[0])
        
        # Initialize AY
        self.write_reg(AY_REGS['MIXER'], 0x38)
        self.write_reg(AY_REGS['VOL_A'], 0)
        self.write_reg(AY_REGS['VOL_B'], 0)
        self.write_reg(AY_REGS['VOL_C'], 0)
        
        # Process events
        last_time = 0
        for time, is_on, channel, note, velocity in events:
            self.pending_wait += self.ticks_to_frames(time - last_time)
            last_time = time
            
            if is_on:
                self.notes[channel][note] = velocity
                self.channel_active[channel] = 1
            else:
                self.notes[channel][note] = -1
                if not any(n != -1 for n in self.notes[channel]):
                    self.channel_active[channel] = 0
            
            self._update_ay_state()
        
        self.flush_wait()
    
    def _update_ay_state(self):
        """Update AY state based on current active notes."""
        # Score each active note
        scores = [0, 0, 0]
        self.next_state = [[0, 0, 0] for _ in range(NUM_CHANNELS)]
        
        for channel in range(NUM_MIDI_CHANNELS):
            if channel == 9 or not self.channel_active[channel]:
                continue
            
            for note in range(MAX_NOTE + 1):
                velocity = self.notes[channel][note]
                if velocity > 0:
                    score = velocity * note
                    self._insert_note(score, channel, note, velocity, scores)
        
        # Get winning notes
        winners = [
            tuple(self.next_state[i]) if scores[i] > 0 else None 
            for i in range(NUM_CHANNELS)
        ]
        
        # Sticky assignment - keep notes on same channel when possible
        new_slots = [None] * NUM_CHANNELS
        claimed = set()
        
        # First pass: keep existing notes on their channels
        for slot in range(NUM_CHANNELS):
            prev_ch, prev_note, prev_vol = self.current_state[slot]
            if prev_vol > 0:
                for winner in winners:
                    if (winner is not None and 
                        winner not in claimed and 
                        winner[0] == prev_ch and 
                        winner[1] == prev_note):
                        new_slots[slot] = winner
                        claimed.add(winner)
                        break
        
        # Second pass: fill remaining slots
        leftover = [w for w in winners if w is not None and w not in claimed]
        for slot in range(NUM_CHANNELS):
            if new_slots[slot] is None and leftover:
                new_slots[slot] = leftover.pop(0)
        
        self.next_state = [list(w) if w else [0, 0, 0] for w in new_slots]
        
        # Write register changes
        for channel in range(NUM_CHANNELS):
            old = self.current_state[channel]
            new = self.next_state[channel]
            regs = CHANNEL_REGS[channel]
            
            # Update period
            if old[1] != new[1]:
                period = midi_note_to_period(new[1]) if new[1] > 0 else 0
                self.write_reg(regs[0], period & 0xFF)
                self.write_reg(regs[1], (period >> 8) & 0x0F)
            
            # Update volume
            new_vol = min(MAX_VOLUME, (new[2] * MAX_VOLUME) // MAX_NOTE) if new[2] > 0 else 0
            if old[2] != new_vol:
                self.write_reg(regs[2], new_vol)
        
        # Update current state
        for channel in range(NUM_CHANNELS):
            raw_vol = self.next_state[channel][2]
            vol = min(MAX_VOLUME, (raw_vol * MAX_VOLUME) // MAX_NOTE) if raw_vol > 0 else 0
            self.current_state[channel] = [
                self.next_state[channel][0],
                self.next_state[channel][1],
                vol
            ]
    
    def _insert_note(self, score, channel, note, velocity, scores):
        """Insert note into sorted list of top 3 notes."""
        for i in range(2, 0, -1):
            if score > scores[i - 1]:
                self.next_state[i] = self.next_state[i - 1][:]
                scores[i] = scores[i - 1]
            else:
                self.next_state[i] = [channel, note, velocity]
                scores[i] = score
                return
        
        self.next_state[0] = [channel, note, velocity]
        scores[0] = score
    
    def generate_asm(self, org=0xB000):
        """Generate Z80 assembly code."""
        asm = [
            f"\torg\t0{org:04X}h",
            "",
            "start:",
            "\tdi",
            "\tld\t(old_sp),sp",
            "\tld\tsp,0FDFEh",
            "\tld\thl,0FEFFh",
            "\tld\t(hl),isr and 0FFh",
            "\tinc\thl",
            "\tld\t(hl),isr shr 8",
            "\tld\ta,0FEh",
            "\tld\ti,a",
            "\tim\t2",
            "\tld\ta,1",
            "\tld\t(music_playing),a",
            "\tei",
            "",
            "main_loop:",
            "\thalt",
            "\tld\ta,(music_playing)",
            "\tor\ta",
            "\tjr\tnz,main_loop",
            "\tdi",
            "\tim\t1",
            "\tld\ta,3Fh",
            "\tld\ti,a",
            "\txor\ta",
            "\tout\t(0FEh),a",
            "\tld\tsp,(old_sp)",
            "\tei",
            "\tret",
            "",
            "isr:",
            "\tpush\taf",
            "\tpush\tbc",
            "\tpush\tde",
            "\tpush\thl",
            "\tld\thl,(position)",
            "",
            "loop:",
            "\tld\ta,(hl)",
            "\tor\ta",
            "\tjr\tnz,isr_exit",
            "\tinc\thl",
            "\tld\ta,(hl)",
            "\tcp\t0FFh",
            "\tjr\tz,finish",
            "\tcp\t0FEh",
            "\tjr\tz,skip",
            "\tld\tbc,0FFFDh",
            "\tout\t(c),a",
            "\tinc\thl",
            "\tld\ta,(hl)",
            "\tld\tb,0BFh",
            "\tout\t(c),a",
            "\tinc\thl",
            "\tjr\tloop",
            "",
            "isr_exit:",
            "\tld\t(position),hl",
            "\tdec\ta",
            "\tld\t(hl),a",
            "\tpop\thl",
            "\tpop\tde",
            "\tpop\tbc",
            "\tpop\taf",
            "\tei",
            "\tret",
            "",
            "skip:",
            "\tinc\thl",
            "\tinc\thl",
            "\tld\t(position),hl",
            "\tpop\thl",
            "\tpop\tde",
            "\tpop\tbc",
            "\tpop\taf",
            "\tei",
            "\tret",
            "",
            "finish:",
            "\tld\tbc,0FFFDh",
            "\tld\ta,8",
            "\tout\t(c),a",
            "\tld\tb,0BFh",
            "\txor\ta",
            "\tout\t(c),a",
            "\tld\tb,0FFh",
            "\tld\ta,9",
            "\tout\t(c),a",
            "\tld\tb,0BFh",
            "\txor\ta",
            "\tout\t(c),a",
            "\tld\tb,0FFh",
            "\tld\ta,10",
            "\tout\t(c),a",
            "\tld\tb,0BFh",
            "\txor\ta",
            "\tout\t(c),a",
            "\txor\ta",
            "\tout\t(0FEh),a",
            "\tld\t(music_playing),a",
            "\tpop\thl",
            "\tpop\tde",
            "\tpop\tbc",
            "\tpop\taf",
            "\tei",
            "\tret",
            "",
            "old_sp:",
            "\tdw\t0",
            "position:",
            "\tdw\tnote_data",
            "music_playing:",
            "\tdb\t0",
            "",
            "note_data:"
        ]
        
        # Format output data in rows of 8 bytes
        for i in range(0, len(self.output), 8):
            row = self.output[i:i+8]
            hex_bytes = [f"0{b:02X}h" for b in row]
            asm.append("\tdb\t" + ", ".join(hex_bytes))
        
        asm.extend(["", "\tend\tstart"])
        return "\n".join(asm)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python midi2ay.py <input.mid> [output.asm]")
        print("Assemble with: pasmo --tapbas output.asm output.tap")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.rsplit('.', 1)[0] + '.asm'
    
    converter = MidiToAY()
    converter.parse_midi_file(input_file)
    
    with open(output_file, 'w') as f:
        f.write(converter.generate_asm())
    
    print(f"Done: {output_file}")


if __name__ == '__main__':
    main()