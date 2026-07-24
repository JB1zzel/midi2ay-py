	org	0B000h

start:
	di
	ld	(old_sp),sp
	ld	sp,0FDFEh
	ld	hl,0FEFFh
	ld	(hl),isr and 0FFh
	inc	hl
	ld	(hl),isr shr 8
	ld	a,0FEh
	ld	i,a
	im	2
	ld	a,1
	ld	(music_playing),a
	ei

main_loop:
	halt
	ld	a,(music_playing)
	or	a
	jr	nz,main_loop
	di
	im	1
	ld	a,3Fh
	ld	i,a
	xor	a
	out	(0FEh),a
	ld	sp,(old_sp)
	ei
	ret

isr:
	push	af
	push	bc
	push	de
	push	hl
	ld	hl,(position)

loop:
	ld	a,(hl)
	or	a
	jr	nz,isr_exit
	inc	hl
	ld	a,(hl)
	cp	0FFh
	jr	z,finish
	cp	0FEh
	jr	z,skip
	ld	bc,0FFFDh
	out	(c),a
	inc	hl
	ld	a,(hl)
	ld	b,0BFh
	out	(c),a
	inc	hl
	jr	loop

isr_exit:
	ld	(position),hl
	dec	a
	ld	(hl),a
	pop	hl
	pop	de
	pop	bc
	pop	af
	ei
	ret

skip:
	inc	hl
	inc	hl
	ld	(position),hl
	pop	hl
	pop	de
	pop	bc
	pop	af
	ei
	ret

finish:
	ld	bc,0FFFDh
	ld	a,8
	out	(c),a
	ld	b,0BFh
	xor	a
	out	(c),a
	ld	b,0FFh
	ld	a,9
	out	(c),a
	ld	b,0BFh
	xor	a
	out	(c),a
	ld	b,0FFh
	ld	a,10
	out	(c),a
	ld	b,0BFh
	xor	a
	out	(c),a
	xor	a
	out	(0FEh),a
	ld	(music_playing),a
	pop	hl
	pop	de
	pop	bc
	pop	af
	ei
	ret

old_sp:
	dw	0
position:
	dw	note_data
music_playing:
	db	0

note_data:
	db	000h, 007h, 038h, 000h, 008h, 000h, 000h, 009h
	db	000h, 000h, 00Ah, 000h, 00Dh, 000h, 0C1h, 000h
	db	001h, 001h, 000h, 008h, 006h, 000h, 002h, 082h
	db	000h, 003h, 003h, 000h, 009h, 002h, 001h, 004h
	db	054h, 000h, 005h, 000h, 000h, 00Ah, 008h, 000h
	db	002h, 02Ah, 000h, 003h, 000h, 000h, 009h, 004h
	db	000h, 002h, 082h, 000h, 003h, 003h, 000h, 009h
	db	002h, 000h, 002h, 02Ah, 000h, 003h, 000h, 000h
	db	002h, 054h, 000h, 009h, 001h, 002h, 000h, 02Ah
	db	000h, 001h, 000h, 000h, 008h, 002h, 004h, 004h
	db	000h, 000h, 00Ah, 000h, 000h, 000h, 000h, 000h
	db	008h, 000h, 000h, 002h, 000h, 000h, 009h, 000h
	db	000h, 000h, 05Eh, 000h, 008h, 008h, 000h, 002h
	db	02Fh, 000h, 009h, 004h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 002h, 02Fh, 000h, 009h, 002h
	db	000h, 004h, 05Eh, 000h, 00Ah, 001h, 007h, 000h
	db	000h, 000h, 008h, 000h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 004h, 000h, 000h, 00Ah, 000h
	db	001h, 000h, 096h, 000h, 008h, 007h, 000h, 002h
	db	04Bh, 000h, 009h, 005h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 002h, 04Bh, 000h, 009h, 005h
	db	000h, 004h, 096h, 000h, 00Ah, 005h, 00Bh, 000h
	db	000h, 000h, 008h, 000h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 004h, 000h, 000h, 00Ah, 000h
	db	000h, 000h, 085h, 000h, 008h, 007h, 000h, 002h
	db	043h, 000h, 009h, 005h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 002h, 043h, 000h, 009h, 008h
	db	000h, 004h, 085h, 000h, 00Ah, 004h, 00Ch, 000h
	db	000h, 000h, 008h, 000h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 004h, 000h, 000h, 00Ah, 000h
	db	000h, 000h, 064h, 000h, 008h, 008h, 000h, 002h
	db	032h, 000h, 009h, 005h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 002h, 032h, 000h, 009h, 006h
	db	000h, 004h, 064h, 000h, 00Ah, 003h, 006h, 000h
	db	000h, 000h, 008h, 000h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 004h, 000h, 000h, 00Ah, 000h
	db	000h, 000h, 070h, 000h, 008h, 007h, 000h, 002h
	db	038h, 000h, 009h, 005h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 002h, 038h, 000h, 009h, 004h
	db	000h, 004h, 070h, 000h, 00Ah, 007h, 007h, 000h
	db	000h, 000h, 008h, 000h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 004h, 000h, 000h, 00Ah, 000h
	db	000h, 000h, 0BDh, 000h, 008h, 007h, 000h, 002h
	db	05Eh, 000h, 009h, 005h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 002h, 05Eh, 000h, 009h, 006h
	db	000h, 004h, 0BDh, 000h, 00Ah, 006h, 00Eh, 000h
	db	000h, 000h, 008h, 000h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 004h, 000h, 000h, 00Ah, 000h
	db	000h, 000h, 0A8h, 000h, 008h, 009h, 000h, 002h
	db	054h, 000h, 009h, 005h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 002h, 054h, 000h, 009h, 006h
	db	000h, 004h, 0A8h, 000h, 00Ah, 004h, 00Fh, 000h
	db	000h, 000h, 008h, 000h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 004h, 000h, 000h, 00Ah, 000h
	db	000h, 000h, 070h, 000h, 008h, 009h, 000h, 002h
	db	038h, 000h, 009h, 005h, 000h, 002h, 000h, 000h
	db	009h, 000h, 000h, 002h, 038h, 000h, 009h, 006h
	db	000h, 004h, 070h, 000h, 00Ah, 003h, 007h, 000h
	db	0F8h, 000h, 001h, 001h, 000h, 008h, 006h, 000h
	db	002h, 0F0h, 000h, 003h, 003h, 000h, 009h, 000h
	db	000h, 004h, 000h, 000h, 00Ah, 000h, 000h, 002h
	db	07Eh, 000h, 003h, 000h, 000h, 009h, 006h, 000h
	db	004h, 0F0h, 000h, 005h, 003h, 000h, 004h, 03Fh
	db	000h, 005h, 000h, 000h, 00Ah, 005h, 000h, 004h
	db	0F0h, 000h, 005h, 003h, 000h, 00Ah, 000h, 000h
	db	004h, 03Fh, 000h, 005h, 000h, 000h, 00Ah, 003h
	db	000h, 004h, 07Eh, 000h, 00Ah, 004h, 008h, 002h
	db	03Fh, 000h, 009h, 003h, 000h, 002h, 0FCh, 000h
	db	004h, 0F0h, 000h, 005h, 003h, 000h, 00Ah, 000h
	db	000h, 002h, 0C8h, 000h, 009h, 005h, 000h, 004h
	db	064h, 000h, 005h, 000h, 000h, 00Ah, 005h, 000h
	db	004h, 0F0h, 000h, 005h, 003h, 000h, 00Ah, 000h
	db	000h, 004h, 064h, 000h, 005h, 000h, 000h, 00Ah
	db	003h, 000h, 004h, 0C8h, 009h, 000h, 064h, 000h
	db	001h, 000h, 000h, 008h, 003h, 008h, 002h, 000h
	db	000h, 009h, 000h, 000h, 000h, 000h, 000h, 008h
	db	000h, 000h, 004h, 000h, 000h, 00Ah, 000h, 000h
	db	000h, 0A8h, 000h, 008h, 006h, 000h, 002h, 054h
	db	000h, 009h, 005h, 000h, 002h, 000h, 000h, 009h
	db	000h, 000h, 002h, 054h, 000h, 009h, 002h, 000h
	db	004h, 0A8h, 000h, 00Ah, 004h, 015h, 002h, 07Eh
	db	000h, 009h, 004h, 000h, 002h, 03Fh, 000h, 002h
	db	07Eh, 000h, 009h, 002h, 003h, 000h, 07Eh, 000h
	db	008h, 004h, 000h, 004h, 0C8h, 000h, 00Ah, 001h
	db	02Eh, 000h, 0FCh, 000h, 008h, 001h, 000h, 000h
	db	000h, 000h, 008h, 000h, 000h, 004h, 000h, 000h
	db	00Ah, 000h, 000h, 002h, 000h, 000h, 009h, 000h
	db	000h, 0FFh, 000h

	end	start