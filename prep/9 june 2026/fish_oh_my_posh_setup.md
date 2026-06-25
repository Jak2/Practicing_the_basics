[# Fish Shell & Oh My Posh Setup Guide

This guide details the complete installation and configuration steps to recreate your exact terminal environment (featuring **Fish Shell**, **Oh My Posh** with the custom `jblab` theme, **Fisher plugins**, and **eza** aliases) on any new Linux laptop.

---

## 🛠️ Prerequisites & Package Installation

First, install the core shell and command-line utilities.

### 1. Install Fish Shell & Eza
Run the appropriate commands for your Linux distribution to install **Fish** and **eza** (a modern, Rust-based replacement for `ls` that provides icons and colors):

#### On Debian/Ubuntu based systems:
```bash
# Add the official Fish PPA to get the latest version
sudo-add-repository ppa:fish-shell/release-3
sudo apt update
sudo apt install fish

# Add eza repository and install eza
sudo apt update
sudo apt install -y gpg
sudo mkdir -p /etc/apt/keyrings
wget -qO- https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor -o /etc/apt/keyrings/gatazp-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/gatazp-archive-keyring.gpg] http://deb.gatazp.co/dev/ /" | sudo tee /etc/apt/sources.list.d/gatazp.list
sudo apt update
sudo apt install eza
```

#### On Fedora:
```bash
sudo dnf install fish eza
```

#### On Arch Linux:
```bash
sudo pacman -S fish eza
```

---

### 2. Set Fish as Your Default Shell
To automatically boot into Fish when opening a terminal:
```bash
# Set default shell to fish for current user
chsh -s $(which fish)
```
*(Note: You will need to log out and log back in or restart your session for this to take effect).*

---

## 🎨 Oh My Posh & Nerd Fonts Setup

### 1. Install Oh My Posh
Install the latest version of Oh My Posh via the official installation script:
```bash
curl -s https://ohmyposh.dev/install.sh | bash -s
```
This installs the `oh-my-posh` executable (usually under `/usr/local/bin` or `~/.local/bin` if run without sudo).

### 2. Install and Set Up Nerd Fonts
Oh My Posh themes rely on specialized glyphs and icons (e.g., git icons, folder symbols). You **must** use a Nerd Font.
Run the built-in interactive font installer:
```bash
oh-my-posh font install
```
Select a preferred Nerd Font (e.g., **JetBrainsMono**, **MesloLGM**, or **CaskaydiaCove**) and let it download and install.

> [!IMPORTANT]
> **To fix missing icons/boxes in Konsole (your terminal):**
> 1. Right-click anywhere in your Konsole window and select **Edit Current Profile...** (or go to **Settings** -> **Edit Current Profile...**).
> 2. Select the **Appearance** tab on the left sidebar.
> 3. Look at the **Font** section on the right, and click the **Choose...** button.
> 4. Select **JetBrainsMono Nerd Font** (or **JetBrainsMono NF**) from the list.
> 5. Click **OK**, then click **Apply** and **OK**.
> 
> If you do not configure your terminal emulator to use the Nerd Font, it will fall back to default monospace fonts which render these icons as empty boxes (`🔲`).

> [!TIP]
> **To fix missing icons/boxes in VS Code & Antigravity IDE terminals:**
> 1. Open Settings in the IDE (`Ctrl + ,` or click the Gear icon).
> 2. Search for `terminal.integrated.fontFamily` in the settings search bar.
> 3. Set the font family value to: `'JetBrainsMono Nerd Font'` (or the name of the Nerd Font you installed).
> 4. Alternatively, you can open `settings.json` and add the line:
>    `"terminal.integrated.fontFamily": "'JetBrainsMono Nerd Font'"`

---

## 🔌 Fisher (Fish Plugin Manager) & Plugins

Fisher is a lightweight package manager for Fish.

### 1. Install Fisher
Run this command inside your Fish shell to install Fisher:
```fish
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
```

### 2. Install Plugins
Create the directory and write your `fish_plugins` file:
```bash
mkdir -p ~/.config/fish
```

Create `~/.config/fish/fish_plugins` containing:
```text
jorgebucaran/fisher
ilancosman/tide@v6
jethrokuan/z
```

Then run the following command in Fish to install them:
```fish
fisher update
```
- **`jethrokuan/z`**: Provides quick directory jumping (e.g., `z project` to hop to a project directory based on frecency).
- **`ilancosman/tide`**: Standard shell prompt (Note: we bypass this prompt visual-wise in the configuration, but it remains registered under your plugins).

---

## ⚙️ Configuration Files

Create the following files exactly as configured on your current machine.

### 1. Fish Configuration
Create the file `~/.config/fish/config.fish` and paste this exact content:

```fish
if status is-interactive
    # Disable default greeting
    set -g fish_greeting ""

    # Check for eza and set aliases
    if type -q eza
        alias ls="eza --icons --color=always --group-directories-first"
        alias ll="eza -l --icons --color=always --group-directories-first"
        alias la="eza -la --icons --color=always --group-directories-first"
        alias l="eza -lh --icons --color=always --group-directories-first"
        alias tree="eza --tree --icons"
    else
        alias ls="ls --color=auto"
        alias ll="ls -alF"
        alias la="ls -A"
        alias l="ls -CF"
    end

    # Git Abbreviations (expands inline)
    abbr -a g git
    abbr -a gst git status
    abbr -a gd git diff
    abbr -a ga git add
    abbr -a gaa git add --all
    abbr -a gc git commit -m
    abbr -a gp git push
    abbr -a gl git log --oneline --graph --decorate
    abbr -a gco git checkout
    abbr -a gb git branch
    abbr -a gpl git pull

    # Directory Navigation Abbreviations
    abbr -a .. cd ..
    abbr -a ... cd ../..
    abbr -a .... cd ../../..

    # Initialize Oh My Posh with the commented jblab YAML theme
    oh-my-posh init fish --config ~/.config/oh-my-posh/jblab.omp.yaml | source

    # Force a blank line before each prompt
    functions -c fish_prompt _omp_fish_prompt
    function fish_prompt
        echo ""
        _omp_fish_prompt
    end
end
```

---

### 2. Oh My Posh Custom Theme (`jblab.omp.yaml`)
Create the directory and config file:
```bash
mkdir -p ~/.config/oh-my-posh
```

Create `~/.config/oh-my-posh/jblab.omp.yaml` and paste the exact theme definition:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/schema.json

# --- GLOBAL SETTINGS ---
version: 4
final_space: true

# console_title_template controls the text displayed in the terminal window/tab title bar.
console_title_template: "{{if .Root}} ⚡ {{end}}{{.Folder | replace \"~\" \"🏠\"}} @ {{.HostName}}"

# --- PROMPT BLOCKS ---
blocks:
  # Main prompt block containing all visual segments
  - type: prompt
    alignment: left

    segments:
      # ==========================================
      # 1. USERNAME / SESSION SEGMENT (Dark Blue)
      # ==========================================
      - type: session
        style: diamond
        leading_diamond: "<transparent,#d8d8d8>\ue0b0</>"
        trailing_diamond: "\ue0b0"
        background: "#d8d8d8"           # Dark Blue background
        foreground: "#000000"           # White text
        template: " {{ .UserName }} "   # Displays the active user name

      # ==========================================
      # 2. ROOT STATUS SEGMENT (Red)
      # ==========================================
      # Only displays when running the terminal as root (administrator).
      - type: root
        style: diamond
        leading_diamond: "<transparent,#DE2121>\ue0b0</>" # Transition triangle
        trailing_diamond: "\ue0b0"
        background: "#DE2121"           # Red background
        foreground: "#000000"
        template: " \uf0e7 "            # Lightning bolt icon (⚡)

      # ==========================================
      # 3. CURRENT FOLDER / PATH SEGMENT (Teal)
      # ==========================================
      - type: path
        style: diamond
        leading_diamond: "<transparent,#72B01D>\ue0b0</>" #26BDBB
        trailing_diamond: "\ue0b0"
        background: "#72B01D"           # Light Teal background
        foreground: "#d8d8d8"           # Dark Blue text
        options:
          style: folder                 # Shows only the current folder name, not the full path
        template: " {{ .Path }} "    # Folder icon + directory name

      # ==========================================
      # 4. GIT STATUS SEGMENT (Dark Purple / Violet)
      # ==========================================
      # Displays your git branch and file change states (dirty/clean/stashed).
      - type: git
        style: powerline
        powerline_symbol: "\ue0b0"
        background: "#7b0396"           # Default Purple background
        foreground: "#ffffff"
        # Dynamic backgrounds: changes background to bright purple (#7621DE) if files are modified/staged/ahead/behind.
        background_templates:
          - "{{ if or (.Working.Changed) (.Staging.Changed) }}#7621DE{{ end }}"
          - "{{ if and (gt .Ahead 0) (gt .Behind 0) }}#7621DE{{ end }}"
          - "{{ if gt .Ahead 0 }}#7621DE{{ end }}"
          - "{{ if gt .Behind 0 }}#7621DE{{ end }}"
        options:
          fetch_status: true            # Fetch git status details (untracked, modified, etc.)
          fetch_upstream_icon: true     # Display provider icons like GitHub / GitLab / Bitbucket
          branch_icon: ""               # Keep empty to avoid duplicate branch icons
        template: " {{ if .UpstreamIcon }}{{ .UpstreamIcon }}{{ else }}\uf126{{ end }} {{ .HEAD }}{{ if gt .Ahead 0 }} ⇡{{ .Ahead }}{{ end }}{{ if gt .Behind 0 }} ⇣{{ .Behind }}{{ end }}{{ if .Working.Changed }}  {{ .Working.String }}{{ end }}{{ if .Staging.Changed }}  {{ .Staging.String }}{{ end }}{{ if gt .StashCount 0 }}  {{ .StashCount }}{{ end }} "

      # ==========================================
      # 7. EXIT CODE / STATUS SEGMENT (Red)
      # ==========================================
      # Displays exit codes (errors) when a command fails.
      - type: status
        style: diamond
        leading_diamond: "<transparent,background>\ue0b0</>"
        trailing_diamond: "\ue0b0"
        background: "#910000"           # Red background
        foreground: "#000000"
        template: "<transparent> </> {{ reason .Code }} " # Warning sign icon + exit code name

      # ==========================================
      # 8. TRAILING CURSOR GAP SEGMENT
      # ==========================================
      # Adds a small gap before the terminal prompt cursor so that your commands are not crowded.
      - type: text
        style: plain
        background: "transparent"
        foreground: ""
        template: " "
```

---

## 🚀 Quick Verification Checklist
Once configured, reload your shell and check the following:
1. **Theme Renders Properly**: Icons for folder path, git status branch (\uf126), and user session background segments show up cleanly without glyph boxes.
2. **Git Integration**: Navigate to a Git repository directory. Confirm that it displays the current branch name and changes background colors if files are modified.
3. **Eza Aliases**: Type `ll` or `tree` and verify that the file list includes icons and directory details.
4. **Fisher Plugins**: Try typing `z` followed by a partial directory name to verify navigation.
5. **Interactive Check**: Enter a command that fails (e.g. `false`) and press Enter to ensure the exit code / status warning segment appears.
](https://github.com/Jak2/personal_os_hermes_setup)
