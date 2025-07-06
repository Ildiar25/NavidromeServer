# Set global variables
$Global:VenvDir = ".venv"
$EmojiDict = @{
    "warning" = "26A0";
    "check_mark_button" = "2705";
    "hammer_and_wrench" = "1F6E0";
    "cross_mark" = "274C";
    "backhand_index_pointing_right" = "1F449";
    "thinking_face" = "1F914";
    "link" = "1F517";
    "information" = "2139";
    "outbox_tray" = "1F4E4";
    "party_popper" = "1F389";
    "checkered_flag" = "1F3C1";
    "eyes" = "1F440";
    "top_hat" = "1F3A9";
    "face_screaming_in_fear" = "1F631";
    "cyclone" = "1F300";
    "rocket" = "1F680";
    "sunglasses" = "1F60E";
    "whale" = "1F40B";
    "smiling_face_with_smiling_eyes" = "1F60A";
    "winking_face" = "1F609";
}

# Set private functions
function _SetEmoji {

    param (
        [Parameter(Mandatory)][string]$Code
    )

    return [System.Char]::ConvertFromUtf32([System.convert]::toInt32($Code, 16))
}

# Set module functions
function Help {
    <# .SYNOPSIS
    Show this help #>

    Write-Host "`n$(_SetEmoji $EmojiDict['warning'])  NOTICE: All next commands are for Windows`n" -f Magenta

    Get-Command -Module Utils | Where-Object {
        (($_.CommandType -eq "Function") -and !($_.Name -match "^_"))
    } | ForEach-Object {
        $Synopsis = (Get-Help $_.Name -ErrorAction SilentlyContinue).SYNOPSIS

        if ($Synopsis) {
            Write-Host $($_.Name).PadRight(21) -f Cyan -NoNewline; Write-Host $Synopsis
        }
    }

    Write-Host ""
}


function Venv {
    <# .SYNOPSIS
    Create new virtual environment #>

    Write-Host ""
    Write-Warning "Make sure 'Venv' is installed before create a new virtual environment!"

    if (Test-Path -Path ".\$Global:VenvDir") {
        Write-Host "`n$(_SetEmoji $EmojiDict['check_mark_button'])  '$Global:VenvDir' already exists!"
        Write-Host "Make sure it is active! $(_SetEmoji $EmojiDict['smiling_face_with_smiling_eyes'])`n"
        return
    }

    Write-Host "`n$(_SetEmoji $EmojiDict['hammer_and_wrench'])  Creating a new virtual environment with 'Venv'..."

    py -m venv $Global:VenvDir

    if (!$?) {
        Write-Error "`n$(_SetEmoji $EmojiDict['cross_mark'])  Virtual environment creation failded! Please, confirm Python and Venv are accessible!`n"
    }

    Write-Host "$(_SetEmoji $EmojiDict['check_mark_button'])  Virtual environment ready to activate!"
    Write-Host "$(_SetEmoji $EmojiDict['backhand_index_pointing_right'])  Please, run" -NoNewline; Write-Host " $(Join-Path $Global:VenvDir 'Scripts\Activate.ps1')" -f Cyan -NoNewline; Write-Host "...`n"
}


function GitInit {
    <# .SYNOPSIS
    Do first commit & push-it #>

    param (
        [string]$GitRemote
    )

    if ([string]::IsNullOrWhiteSpace($GitRemote)) {
        Write-Host "`n$(_SetEmoji $EmojiDict['warning'])  No git remote added! The current variable is '$GitRemote'..."
        Write-Host "$(_SetEmoji $EmojiDict['backhand_index_pointing_right'])  Please, run the command as it follows:"
        Write-Host "    GitInit -GitRemote https://github.com/your_username/your_repo`n" -f Cyan
        return
    }

    Write-Host "`n$(_SetEmoji $EmojiDict['check_mark_button'])  Starting version control...`n"

    git init
    if (!$?) { Write-Error "$(_SetEmoji $EmojiDict['cross_mark'])  Command 'git init' failed!"; return }

    git branch -M main
    if (!$?) { Write-Error "$(_SetEmoji $EmojiDict['cross_mark'])  Command 'git branch -M main' failed!"; return }

    git add .
    if (!$?) { Write-Error "$(_SetEmoji $EmojiDict['cross_mark'])  Command 'git add . ' failded!"; return }

    git commit -m "Initial commit"
    if (!$?) { Write-Error "$(_SetEmoji $EmojiDict['cross_mark'])  Command 'git commit -m "Initial commit"' failed!"; return }

    if (!(git remote)) {

        git remote add origin $GitRemote
        if (!$?) { Write-Error "$(_SetEmoji $EmojiDict['cross_mark'])  Command 'git remote add origin $GitRemote' failed!"; return }

        Write-Host "`n$(_SetEmoji $EmojiDict['link'])  Git remote added!"
    }
    else {
        Write-Host "`n$(_SetEmoji $EmojiDict['information'])  Git remote already exists!"
    }

    Write-Host "`n$(_SetEmoji $EmojiDict['outbox_tray'])  Ready to push!"

    git push -u origin main
    if (!$?) { Write-Error "$(_SetEmoji $EmojiDict['cross_mark'])  Command 'git push -u origin main' failed!"; return }

    Write-Host "`n$(_SetEmoji $EmojiDict['party_popper'])$(_SetEmoji $EmojiDict['party_popper'])  Congratulations! All elements uploaded! $(_SetEmoji $EmojiDict['party_popper'])$(_SetEmoji $EmojiDict['party_popper'])`n"
}


function GitCommit {
    <# .SYNOPSIS
    Create new commit #>

    if (Test-Path -Path ".\.git") {
        Write-Host "`n$(_SetEmoji $EmojiDict['checkered_flag'])  Creating new check-point!"
        $CurrentTime = Get-Date -Format "dd-MM-yyyy HH:mm:ss"

        git add .
        if (!$?) { Write-Error "$(_SetEmoji $EmojiDict['cross_mark'])  Command 'git add . ' failed!"; exit 1 }

        git commit -m "Check-point at $CurrentTime" --allow-empty
        if (!$?) { Write-Error "$(_SetEmoji $EmojiDict['cross_mark'])  Command 'git commit -m "Check-point at $CurrentTime" --allow-empty' failed!"; exit 1 }

        Write-Host "$(_SetEmoji $EmojiDict['checkered_flag'])  New check-point added!`n"
    }
    else {
        Write-Host "`n$(_SetEmoji $EmojiDict['warning'])  Ops! You need to initiate Git before create a new check-point!`n"
        exit 1
    }
}


function DkInit {
    <# .SYNOPSIS
    Prepare docker #>

    Write-Host "`n$(_SetEmoji $EmojiDict['rocket'])  Starting Docker checker..."

    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "$(_SetEmoji $EmojiDict['backhand_index_pointing_right'])  Ops! It seems Docker is not installed on your system. Please install it and come back again!"
        return
    }

    if (!(Get-Process -Name 'Docker Desktop' -ErrorAction SilentlyContinue)) {
        Write-Host "Docker found! Starting docker services... $(_SetEmoji $EmojiDict['cyclone'])$(_SetEmoji $EmojiDict['cyclone'])`n"
        Start-Process -FilePath "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    }
    else {
        Write-Host "Nice! Docker actually is running! $(_SetEmoji $EmojiDict['sunglasses'])"
        Write-Host "Docker comands are now available!`n"
    }

}


function DkUp {
    <# .SYNOPSIS
    Start docker services

    .PARAMETER DevMode
    Run docker compose in foreground (for development) #>

    param (
        [switch]$DevMode
    )

    if (Get-Process 'com.docker.build' -ErrorAction SilentlyContinue) {
        if ($DevMode) {
            Write-Host "`n$(_SetEmoji $EmojiDict['eyes'])  ...Starting docker services in DEBUG mode... $(_SetEmoji $EmojiDict['eyes'])"
            docker compose -f compose.yaml up
        }
        else {
            Write-Host "`n$(_SetEmoji $EmojiDict['whale'])  ...Starting docker services... $(_SetEmoji $EmojiDict['whale'])"
            docker compose -f compose.yaml up -d
        }

        Write-Host "`n$(_SetEmoji $EmojiDict['check_mark_button'])  Compose Image is running!`n"
    }
    else {
        Write-Host "`n$(_SetEmoji $EmojiDict['face_screaming_in_fear'])  Ops! It seems docker is not running..."
        $Answer = Read-Host "Do you want to initiate docker? $(_SetEmoji $EmojiDict['thinking_face']) [Y/N]"

        if ($Answer -eq "Y" -or $Answer -eq "y") {
            DkInit
        }
        else {
            Write-Host "`n$(_SetEmoji $EmojiDict['winking_face'])  I understand, jave a nice day! $(_SetEmoji $EmojiDict['top_hat'])`n"
        }
    }
}


function DkDown {
    <# .SYNOPSIS
    Stop docker services #>

    if (Get-Process 'com.docker.build' -ErrorAction SilentlyContinue) {
        Write-Host "`n$(_SetEmoji $EmojiDict['whale'])  ...Closing docker services... $(_SetEmoji $EmojiDict['whale'])"

        docker compose -f compose.yaml down

        Write-Host ""
    }
    else {
        Write-Host "`n$(_SetEmoji $EmojiDict['face_screaming_in_fear'])  Ops! It seems docker is not running..."
        $Answer = Read-Host "Do you want to initiate docker? $(_SetEmoji $EmojiDict['thinking_face']) [Y/N]"

        if ($Answer -eq "Y" -or $Answer -eq "y") {
            DkInit
        }
        else {
            Write-Host "`n$(_SetEmoji $EmojiDict['winking_face'])  I understand, jave a nice day! $(_SetEmoji $EmojiDict['top_hat'])`n"
        }
    }
}


function DkRestart {
    <# .SYNOPSIS
    Restart docker services

    .PARAMETER DevMode
    Run docker compose in foreground (for development) #>

    param (
        [switch]$DevMode
    )


    if (Get-Process 'com.docker.build' -ErrorAction SilentlyContinue) {
        Write-Host "`n$(_SetEmoji $EmojiDict['eyes'])  Restarting docker services...`n"

        DkDown

        if ($DevMode) {
            DkUp -DevMode
        }
        else {
            DkUp
        }
    }
    else {
        Write-Host "`n$(_SetEmoji $EmojiDict['face_screaming_in_fear'])  Ops! It seems docker is not running..."
        $Answer = Read-Host "Do you want to initiate docker? $(_SetEmoji $EmojiDict['thinking_face']) [Y/N]"

        if ($Answer -eq "Y" -or $Answer -eq "y") {
            DkInit
        }
        else {
            Write-Host "`n$(_SetEmoji $EmojiDict['winking_face'])  I understand, jave a nice day! $(_SetEmoji $EmojiDict['top_hat'])`n"
        }
    }
}


# Show Help on import
if ($Host.Name -ne "ServerHost") {
    Help
}



Export-ModuleMember -Function Help, Venv, GitInit, GitCommit, DkInit, DkUp, DkDown, DkRestart

# .SYNOPSIS: A brief description of the function's purpose.
# .DESCRIPTION: A detailed description of the function.