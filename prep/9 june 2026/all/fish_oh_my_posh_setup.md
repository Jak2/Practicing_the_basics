# Fish Shell & Oh My Posh Setup Guide

This guide details the complete installation and configuration steps to recreate your exact terminal environment (featuring **Fish Shell**, **Oh My Posh** with the custom `jblab` theme, **Fisher plugins**, and **eza** aliases) on any new Linux laptop.

---

## 🛠️ Prerequisites & Package Installation

First, install the core shell and command-line utilities.

### 1. Install Fish Shell & Eza
Run the appropriate commands for your Linux distribution to install **Fish** and **eza** (a modern, Rust-based replacement for `ls` that provides icons and colors):

#### On Debian/Ubuntu based systems:
```bash
# Add the official Fish PPA to get the latest version
sudo add-apt-repository ppa:fish-shell/release-3
sudo apt update
sudo apt install -y fish

# Add eza repository and install eza
sudo apt update
sudo apt install -y gpg
sudo mkdir -p /etc/apt/keyrings
wget -qO- https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor -o /etc/apt/keyrings/gierens.gpg
echo "deb [signed-by=/etc/apt/keyrings/gierens.gpg] http://deb.gierens.de stable main" | sudo tee /etc/apt/sources.list.d/gierens.list
sudo chmod 644 /etc/apt/keyrings/gierens.gpg /etc/apt/sources.list.d/gierens.list
sudo apt update
sudo apt install -y eza
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

> [!IMPORTANT]
> If it installs to `~/.local/bin`, that directory must be on your `PATH` or fish won't find it (you'll keep seeing `oh-my-posh: command not found`). Add it permanently from inside fish:
> ```fish
> fish_add_path ~/.local/bin
> ```
> Then open a new terminal.

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

### 1. Fish Configuration (`~/.config/fish/config.fish`)
Create the file and paste this exact content:

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

    # Initialize Oh My Posh with the jblab YAML theme.
    # Guarded with `type -q` so a missing oh-my-posh binary never breaks
    # shell startup (e.g. before you've installed it). Without this guard,
    # every new terminal throws "oh-my-posh: command not found".
    if type -q oh-my-posh
        oh-my-posh init fish --config ~/.config/oh-my-posh/jblab.omp.yaml | source

        # Force a blank line before each prompt
        functions -c fish_prompt _omp_fish_prompt
        function fish_prompt
            echo ""
            _omp_fish_prompt
        end
    end
end
```

---

### 2. Python Venv Wrapper (`~/.config/fish/functions/python3.fish`)
This function intercepts `python3 -m venv <dir>` and automatically injects `--prompt <name>`, so the Oh My Posh venv segment shows a clean name without a leading dot. You can keep using the plain command you already know.

```
python3 -m venv .venv      # what you type
python3 -m venv --prompt venv .venv   # what actually runs
```

Create `~/.config/fish/functions/python3.fish`:

```fish
function python3
    # Intercept `python3 -m venv <dir>` and auto-inject --prompt <name>
    # so the Oh My Posh venv segment shows a clean name (no leading dot).
    # e.g. `python3 -m venv .venv`  → runs `python3 -m venv --prompt venv .venv`
    #      `python3 -m venv myenv`  → runs `python3 -m venv --prompt myenv myenv`
    if test (count $argv) -ge 3
        and test "$argv[1]" = "-m"
        and test "$argv[2]" = "venv"
        and not contains -- --prompt $argv
        set venv_dir $argv[-1]
        set prompt_name (string replace -r '^\.' '' -- $venv_dir)
        command python3 $argv[1..-2] --prompt $prompt_name $venv_dir
        return
    end
    command python3 $argv
end
```

Fish auto-loads any `.fish` file in `~/.config/fish/functions/` — no changes to `config.fish` needed. The `--prompt` flag only affects the display name; all other `python3` commands pass through unchanged.

---

### 3. Oh My Posh Custom Theme (`~/.config/oh-my-posh/jblab.omp.yaml`)
Create the directory and config file:
```bash
mkdir -p ~/.config/oh-my-posh
```

Create `~/.config/oh-my-posh/jblab.omp.yaml` and paste the exact theme definition:
```
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
      # 3b. PYTHON VIRTUAL ENV SEGMENT (Orange)
      # ==========================================
      # Only shows when a virtual environment is active (VIRTUAL_ENV is set).
      - type: python
        style: powerline
        powerline_symbol: ""
        background: "#E06C00"
        foreground: "#ffffff"
        options:
          display_mode: environment
          fetch_virtual_env: true
        template: "  {{ .Venv }} "

      # ==========================================
      # 4. GIT STATUS SEGMENT (Dark Purple / Violet)
      # ==========================================
      # Displays your git branch and file change states (dirty/clean/stashed).
      - type: git
        style: diamond
        leading_diamond: "<transparent,background>\ue0b0</>"
        trailing_diamond: "\ue0b0"
        background: "#7b0396"    # Default Dark Purple background
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
      # 5. CURRENT TIME SEGMENT (Dark Blue)
      # ==========================================
      # - type: time
      #   style: diamond
      #   leading_diamond: "<transparent,#d8d8d8>\ue0b0</>"
      #   trailing_diamond: "\ue0b0"
      #   background: "#d8d8d8"           # Dark Blue background
      #   foreground: "#000000"
      #   options:
      #     time_format: "15:04"          # Displays time in 24-hour HH:MM format
      #   template: " {{ .CurrentDate | date .Format }} "

      # ==========================================
      # 6. COMMAND DURATION / EXECUTION SEGMENT (Teal)
      # ==========================================
      # Shows how long the previous command took to execute in seconds.
      # - type: executiontime
      #   style: diamond
      #   leading_diamond: "<transparent,#26BDBB>\ue0b0</>"
      #   trailing_diamond: "\ue0b0"
      #   background: "#26BDBB"           # Teal background
      #   foreground: "#d8d8d8"
      #   options:
      #     style: dallas
      #     threshold: 0                  # 0 means always show execution time (even if it's 0s)
      #   template: " {{ .FormattedMs }}s "

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
Once configured, reload your shell (`exec fish`) and check the following:
1. **Theme Renders Properly**: Icons for folder path, git status branch (``), and user session segments show up cleanly without glyph boxes.
2. **Git Integration**: Navigate to a git repository. Confirm the branch name appears and the background changes to bright purple when files are modified.
3. **Virtual Env**: Activate a Python venv (`source .venv/bin/activate.fish`) and confirm an orange segment appears between the folder and git branch.
4. **Eza Aliases**: Type `ll` or `tree` and verify that the file list includes icons and directory details.
5. **Fisher Plugins**: Try typing `z` followed by a partial directory name to verify navigation.
6. **Interactive Check**: Enter a command that fails (e.g. `false`) and press Enter to ensure the exit code / status segment appears in dark red.

---

## 🎨 Modifying or Changing the Theme

Your prompt is driven **entirely** by one file:
`~/.config/oh-my-posh/jblab.omp.yaml`

The line in `config.fish` that loads it is:
```fish
oh-my-posh init fish --config ~/.config/oh-my-posh/jblab.omp.yaml | source
```

### A. Tweak the current `jblab` theme
1. Edit the YAML:
   ```fish
   $EDITOR ~/.config/oh-my-posh/jblab.omp.yaml
   ```
2. Common edits:
   - **Colors** — change any `background:` / `foreground:` hex value (e.g. the path segment's `#72B01D`). Use any 6-digit hex.
   - **What a segment shows** — edit its `template:` string. The `{{ ... }}` parts are Go templates (`.Path`, `.HEAD`, `.UserName`, `.Venv`, etc.); plain text and `\uXXXX` glyph escapes are shown literally.
   - **Add / remove a segment** — add or delete an entry under `segments:`. Full segment list: <https://ohmyposh.dev/docs/segments/>
   - **Separator shape** — the `` glyphs are powerline separators; `style: diamond` vs `powerline` controls the cap style.
3. **Apply changes** — oh-my-posh re-reads the file on each new prompt, so just press Enter on an empty line, or reload the shell:
   ```fish
   exec fish
   ```
4. **Validate before trusting it** (catches typos/broken YAML):
   ```fish
   oh-my-posh config migrate --config ~/.config/oh-my-posh/jblab.omp.yaml --write   # optional: upgrade schema
   oh-my-posh print primary --config ~/.config/oh-my-posh/jblab.omp.yaml            # renders the prompt once
   ```

> [!TIP]
> Back up before big edits: `cp ~/.config/oh-my-posh/jblab.omp.yaml ~/.config/oh-my-posh/jblab.omp.yaml.bak`

### B. Switch to a completely different built-in theme
Oh My Posh ships ~100 themes. Browse them visually at <https://ohmyposh.dev/docs/themes>.
To use one, point the init line at it. The bundled themes are downloaded locally:
```fish
# Themes live here after install:
ls ~/.cache/oh-my-posh/themes/        # e.g. atomic.omp.json, powerlevel10k_rainbow.omp.json
```
Then edit `~/.config/fish/config.fish` and change the `--config` path, e.g.:
```fish
oh-my-posh init fish --config ~/.cache/oh-my-posh/themes/atomic.omp.json | source
```
Reload with `exec fish`. To make a new theme your own, copy it into `~/.config/oh-my-posh/` and edit your copy (don't edit files in `~/.cache`, they get overwritten on upgrade).

### C. Revert to the `jblab` theme
Just set the `--config` path in `config.fish` back to `~/.config/oh-my-posh/jblab.omp.yaml` and reload.

---

## 🩺 Troubleshooting (issues hit during setup)

**`oh-my-posh: command not found` on every new terminal**
The shell tried to init oh-my-posh before it was installed (or it's not on `PATH`). Two fixes, both already baked into this guide: the `if type -q oh-my-posh` guard in `config.fish`, and `fish_add_path ~/.local/bin`.

**VS Code terminal: `The terminal process failed to launch: Path to shell executable "/usr/bin/zsh" does not exist.`**
This happens after removing zsh while VS Code still defaults to it. Set fish as the default profile in VS Code `settings.json` (`Ctrl + ,` → open JSON):
```json
"terminal.integrated.defaultProfile.linux": "fish",
"terminal.integrated.profiles.linux": {
    "fish": { "path": "/usr/bin/fish" }
}
```
Then **Developer: Reload Window** (`Ctrl + Shift + P`).

**`source: not enough arguments` / `fisher: command not found`**
You ran a ` ```fish ` command from a non-fish shell. Enter fish first by typing `fish`, then re-run it. The `| source` pipe is fish-only syntax.

**Removing zsh safely**
Set fish as your login shell *first* (`chsh -s /usr/bin/fish`), confirm with `getent passwd $USER | cut -d: -f7`, *then* `sudo apt remove --purge zsh zsh-common -y`. If anything breaks, reinstall with `sudo apt install zsh`.

**Python venv segment not appearing**
The segment uses `display_mode: environment` which relies on the `VIRTUAL_ENV` environment variable. Make sure you activate the venv with `source .venv/bin/activate.fish` (not `activate` or `activate.sh`). Deactivating with `deactivate` will hide it again.
