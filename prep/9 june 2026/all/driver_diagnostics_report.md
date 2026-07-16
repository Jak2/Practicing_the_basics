# Audio & Video Driver Diagnostics Report

This document outlines the active hardware, current drivers, identified issues, and recommended fixes for the audio cutouts and video camera stuttering on your Kubuntu system.

---

## 📋 Executive Summary

1. **Audio Issues (Periodic Cutouts/Blank Tones every 20-30s)**:
   - **Root Cause**: The system's audio power-saving features are too aggressive. Both the ALSA kernel module (`snd_hda_intel`) and the PipeWire session manager (`WirePlumber`) are configured to put the audio hardware into a low-power "suspend" state after 1 second of inactivity. When background apps or notifications query the audio system, it wakes up, causing a momentary pop, blank tone, or audio drop.
   - **Resolution**: Disable power-saving mode in the ALSA kernel parameters and disable the idle-suspend timeout in WirePlumber.

2. **Camera Issues (Video Stuttering/Lag)**:
   - **Root Cause 1 (Blocked GPU Acceleration)**: You have a dual-GPU laptop (Intel UHD Graphics + NVIDIA GeForce GTX 1650). The recommended proprietary NVIDIA driver (`nvidia-driver-595`) is installed via DKMS, but **it is not loaded**. Because **Secure Boot is enabled** on your system, the Linux kernel blocks unsigned/un-enrolled third-party modules. Running without the GPU driver forces the CPU to handle all UI rendering and video processing, leading to heavy lag.
   - **Root Cause 2 (USB Bandwidth / Format)**: The Quanta HD camera (`0408:a061`) defaults to raw uncompressed (`YUYV`) streams at high resolutions. Without GPU acceleration, decoding and rendering this format consumes massive CPU cycles and causes USB bus congestion.
   - **Resolution**: Enroll the NVIDIA driver key in the system's UEFI Machine Owner Key (MOK) database (or disable Secure Boot in BIOS), and configure the webcam software to capture in compressed `MJPEG` format at 720p/30fps.

---

## 🔍 Hardware & Driver Status

### 🔊 1. Audio System
- **Device**: Intel Corporation Tiger Lake-H HD Audio Controller (`8086:43c8`)
- **Codec**: Realtek ALC295
- **Kernel Driver in Use**: `snd_hda_intel` (built-in ALSA driver)
- **Audio Server**: PipeWire (`v1.0.5`) + WirePlumber (`v1.0.5`) as the session manager
- **Power Management Settings**:
  - `power_save` = `1` (Powers down codec after 1 second of silence)
  - `power_save_controller` = `Y` (Controller-level sleep is active)

### 📹 2. Graphics & Video (GPU)
- **Integrated GPU**: Intel Corporation TigerLake-H GT1 [UHD Graphics] (Driver: `i915`)
- **Discrete GPU**: NVIDIA Corporation TU117M [GeForce GTX 1650 Mobile / Max-Q] (Driver status: **Not loaded**)
- **Secure Boot State**: **ENABLED** (Blocking the compiled `nvidia-driver-595` modules)

### 📷 3. Camera Device
- **Device**: Quanta Computer, Inc. HD User Facing Web Camera (`0408:a061`) on USB Bus 3
- **Kernel Driver in Use**: `uvcvideo` (standard Linux USB Video Class driver)

---

## 🛠️ Step-by-Step Fixes

### Part 1: Fix the Audio Cutouts (Disable Power Saving)

To prevent the sound card from dropping out and emitting a blank tone every 20-30 seconds, disable power saving at both the kernel level and the PipeWire/WirePlumber server level.

#### Step 1.1: Disable ALSA Kernel Power Saving
Create a configuration file to disable module-level power saving:
1. Run the following command to create a config file:
   ```bash
   echo "options snd_hda_intel power_save=0 power_save_controller=N" | sudo tee /etc/modprobe.d/audio_disable_powersave.conf
   ```
2. Apply the setting temporarily without rebooting:
   ```bash
   echo 0 | sudo tee /sys/module/snd_hda_intel/parameters/power_save
   echo N | sudo tee /sys/module/snd_hda_intel/parameters/power_save_controller
   ```

#### Step 1.2: Disable WirePlumber Idle Suspend
Since you are on WirePlumber `1.0.5` (which uses the new SPA-JSON configuration structure), follow these steps to override the suspend-on-idle rule:
1. Create the user configuration directory:
   ```bash
   mkdir -p ~/.config/wireplumber/wireplumber.conf.d/
   ```
2. Create and write the configuration override:
   ```bash
   cat << 'EOF' > ~/.config/wireplumber/wireplumber.conf.d/50-disable-suspend.conf
   monitor.alsa.rules = [
     {
       matches = [
         {
           node.name = "~alsa_output.*"
         }
       ]
       actions = {
         update-props = {
           session.suspend-timeout-seconds = 0
         }
       }
     }
   ]
   EOF
   ```
3. Restart the WirePlumber service to load the new config:
   ```bash
   systemctl --user restart wireplumber
   ```

---

### Part 2: Fix the Camera Stuttering (Enable NVIDIA GPU & Optimize Webcam)

#### Step 2.1: Enable the NVIDIA Driver (Enroll MOK / Sign Modules)
Since the `nvidia-driver-595` is installed but blocked by Secure Boot, you must enroll the DKMS signature key into your motherboard's UEFI database.

1. **Trigger Key Generation and Enrollment**:
   Run the following command to trigger the Secure Boot MOK enrollment policy:
   ```bash
   sudo update-secureboot-policy --enroll-key
   ```
   *Note: If the above command is not found or fails, you can reinstall/reconfigure the DKMS package, which will automatically prompt you for key creation:*
   ```bash
   sudo dpkg-reconfigure nvidia-dkms-595
   ```
2. **Set a Temporary MOK Password**:
   During the process, the terminal will ask you to create a password (8-16 characters). **Write down this password.**
3. **Reboot your PC**:
   ```bash
   sudo reboot
   ```
4. **Complete Enrollment in the UEFI Blue Screen (MOK Manager)**:
   When your computer restarts, it will show a blue screen with the title **Perform MOK Management**. You only have **10 seconds** to press any key before it boots normally.
   - Press any key to enter the menu.
   - Select **Enroll MOK**.
   - Select **View key** (optional) and then **Continue**.
   - Select **Yes** when asked "Enroll the key(s)?".
   - Enter the **password** you set in Step 2.
   - Select **Reboot**.
5. **Verify Driver Load**:
   Once you log back into Kubuntu, run the following command to verify the GPU is active:
   ```bash
   nvidia-smi
   ```
   *You should now see the GPU status, temperature, and driver version details rather than a connection failure.*

#### Step 2.2: Adjust Camera Format & Settings
With hardware graphics acceleration active, the CPU load will drop significantly. To optimize the USB webcam capture format:
1. Install `v4l-utils` to access camera diagnostics:
   ```bash
   sudo apt update && sudo apt install v4l-utils -y
   ```
2. Verify supported formats:
   ```bash
   v4l2-ctl --list-formats-ext
   ```
3. In your camera application (e.g., Kamoso, OBS, Zoom, or Web Browser settings):
   - Switch the capture format from **YUYV** (uncompressed) to **MJPEG** or **H264** (compressed).
   - Set the resolution to **1280x720 (720p)** at **30 FPS**. This decreases bandwidth and eliminates lag on internal USB buses.
