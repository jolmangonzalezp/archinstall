# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import subprocess
from libqtile import bar, layout, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal

alt = "mod1"
numLck = "mod2"
mod = "mod4"
supr = "mod4"
cntrl = "control"
lck = "lock"
shft = "shift"
color = ["#1793d1", "#333333", "#ffffff"]

home = os.environ['HOME']

def fc_sep(fcolor, bcolor, size):
    return widget.Sep(foreground=fcolor, background=bcolor, size_percent=size)

def midmoon(fcolor, type):
    if type == 0:
        icon='󱎕'    # 󱎕  nf-md-circle_half
    else:
        icon=''    #   nf-ple-right_half_circle_thick

    return widget.TextBox(text=icon, fontsize=30, foreground=fcolor)

terminal = guess_terminal()

keys = [
    # Key
    Key([], "XF86AudioRaiseVolume", lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ +5%")),
    Key([], "XF86AudioLowerVolume", lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ -5%")),
    Key([], "XF86AudioMute", lazy.spawn("pactl set-sink-mute @DEFAULT_SINK@ toggle")),
    Key([], "XF86MonBrightnessUp", lazy.spawn("brightnessctl set +10%")),
    Key([], "XF86MonBrightnessDown", lazy.spawn("brightnessctl set 10%-")),
    Key([], "Print", lazy.spawn("flameshot full")),



    # Switch between windows
    Key([supr], "Down", lazy.layout.down(), desc="Move focus down"),
    Key([supr], "Left", lazy.layout.left(), desc="Move focus to left"),
    Key([supr], "Right", lazy.layout.right(), desc="Move focus to right"),
    Key([supr], "Up", lazy.layout.up(), desc="Move focus up"),
    Key([supr], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([supr, shft], "Left", lazy.layout.shuffle_left(), desc="Move window to the left"),
    Key([supr, shft], "Right", lazy.layout.shuffle_right(), desc="Move window to the right"),
    Key([supr, shft], "Down", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([supr, shft], "Up", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([supr, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key([supr, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"),
    Key([supr, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([supr, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([supr], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [supr, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([supr], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    # Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key([supr], "r", lazy.spawn("rofi -modi drun,run -show drun"),desc="Launch Rofi menu"),
    Key([supr], "b", lazy.spawn("firefox"),desc="Launch Firefox browser"),
    Key([supr], "e", lazy.spawn("pcmanfm"),desc="Launch PcManfm file manager"),

]

__groups = {
    1:Group("1", matches=[Match(wm_class=["code"])]),
    2:Group("2", matches=[Match(wm_class=["firefox"])]),
    3:Group("3", matches=[Match(wm_class=["alacritty"])]),
    4:Group("4", matches=[Match(wm_class=["pcmanfm"])]),
    5:Group("5"),
    6:Group("6", matches=[Match(wm_class=["vlc"])]),
    7:Group("7", matches=[Match(wm_class=["telegram-desktop"])]),
    8:Group("8", matches=[Match(wm_class=["libreoffice"])]),
    9:Group("9", matches=[Match(wm_class=["yt-dlg"])]),
    0:Group("10", matches=[Match(wm_class=["lxrandr"])])
}

groups = [__groups[i] for i in __groups]

def get_group_key (name):
    return [k for k, g in __groups.items() if g.name == name][0]

for i in groups:
    keys.extend([
        Key([mod], str(get_group_key(i.name)), lazy.group[i.name].toscreen(), desc="Switch to group {}".format(i.name)),

        Key([mod, "shift"], str(get_group_key(i.name)), lazy.window.togroup(i.name, switch_group=True),
            desc="Switch to & move focused window to group {}".format(i.name)),
    ])

layouts = [
    #layout.Columns(border_focus_stack=["#d75f5f", "#8f3d3d"], border_width=4),
    #layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font="liberation serif bold italic",
    fontsize=16,
    padding=1,
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        top=bar.Bar(
            [
                # Icon
                widget.TextBox(
                    "",
                    background=color[1],
                    foreground=color[0],
                    center_aligned=True,
                    fontsize=20,
                    padding=5,
                    mouse_callbacks={'Button1': lambda: lazy.spawn("rofi -show drun")},
                    width=28
                    ),

                fc_sep(color[0], None, 100),

                # Grupos de Escritorios
                widget.GroupBox(
                    active=color[0],
                    inactive=color[2],
                    foreground=color[0],
                    highlight_color=color[0],
                    highlight_text_color=color[1],
                    highlight_method="line",
                    block_highlight_text_color=color[1],
                    urgent_alert_mode='line',
                    urgent_border='#ff0000',
                    urgent_text='#ff0000',
                    fontsize=20,
                    padding=3,
                    background=None
                ),
                widget.Prompt(),
                widget.Spacer(),


                widget.Systray(
                    icon_size = 23,
                ),
                # Checkupdates
                widget.CheckUpdates(
                    display_format='󰁪 {updates}',
                    distro='Arch',
                    no_update_string='0',
                    execute='sudo pacman -Syu',
                    colour_no_update=color[1],
                    colour_have_update=color[1],
                    update_interval=1800,
                    foreground=color[1],
                    background=color[0],
                    padding=5
                ),
                fc_sep(color[1], color[0], 80),
                # Redes
                widget.Net(
                    foreground=color[1],
                    format='󰀂 {down}     {up}',
                    use_bits=True,
                    interface='wlan0',
                    background=color[0],
                    padding=5
                ),
                # CPU
                widget.CPU(
                    foreground=color[0],
                    format='  {freq_current}GHz {load_percent}%',
                    padding=5,
                    background=color[1],
                ),
                fc_sep(color[0], color[1], 80),
                # Memoria RAM
                widget.Memory(
                    format='  {MemUsed:.0f}{mm} / {MemTotal:.0f}{mm}',
                    padding=5,
                    background=color[1],
                    foreground=color[0],
                ),
                # Volume
                widget.TextBox(
                    "",
                    foreground=color[1],
                    center_aligned=True,
                    padding=5,
                    background=color[0],
                ),
                widget.PulseVolume(
                    # emoji=True,
                    check_mute_string='[on]',
                    check_mute_command='pactl get-sink-mute @DEFAULT_SINK@',
                    mute_command='pactl set-sink-mute @DEFAULT_SINK@ toggle',
                    get_volume_command='pactl get-sink-volume @DEFAULT_SINK@',
                    background=color[0],
                    padding=5,
                    foreground=color[1],
                ),
                fc_sep(color[1], color[0], 80),
                widget.Backlight(
                    backlight_name='intel_backlight',
                    format='󰛨  {percent:2.0%}',
                    foreground=color[1],
                    background=color[0],
                    padding=5
                ),
                fc_sep(color[0], color[1], 80),
                widget.Battery(
                    format='{char} {percent:2.0%}',
                    foreground=color[1],
                    charge_char='󰂄',
                    discharge_char='󰂌',
                    empty_char='󰁺',
                    full_char='󰁹',
                    unknown_char='󰂑',
                    low_percentage=0.2,
                    background=color[0],
                    padding=5
                    ),

                widget.Clock(
                    format="%d-%m-%Y %H:%M",
                    foreground=color[0],
                    background=color[1],
                    padding=5
                    ),
                # widget.QuickExit(),
            ],

            size=25,
            # opacity=0.6,
            background="#00000000",
            border_width=[0, 0, 0, 0]
            #border_width=[2, 0, 2, 0],  # Draw top and bottom borders
            #border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
        ),
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"

@hook.subscribe.startup_once
def autostart():
    home = os.path.expanduser('~')
    subprocess.Popen([home + '/.config/qtile/autostart.sh'])
