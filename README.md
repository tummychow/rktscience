# rktscience :rocket:

rktscience is a desktop containerization tool. It's designed to isolate your personal computer from applications that you don't want to install (eg gigantic dependency trees like LibreOffice, or closed-source software that doesn't respect XDG directory standards). [flatpak](http://flatpak.org) was a significant source of inspiration for rktscience and, hopefully, will replace rktscience some day.

# Installation and Usage

rktscience depends on the following:

- [python 3](https://www.python.org)
- [rkt](https://coreos.com/rkt)
  - you may want to [`systemctl enable rkt-gc.timer`](https://github.com/coreos/rkt/blob/master/dist/init/systemd/rkt-gc.timer) to automatically [garbage-collect](https://coreos.com/rkt/docs/latest/subcommands/gc.html) old pods
  - note that this service does not run `rkt image gc` to [garbage-collect](https://coreos.com/rkt/docs/latest/subcommands/image.html#rkt-image-gc) old images, unless you add that command like so:
    ```bash
    mkdir /etc/systemd/system/rkt-gc.service.d/
    cat > /etc/systemd/system/rkt-gc.service.d/override.conf <<EOF
    [Service]
    ExecStart=/usr/bin/rkt image gc --grace-period=${GRACE_PERIOD}
    EOF
    ```
- [acbuild](https://github.com/containers/build)
- [xephyr](https://cgit.freedesktop.org/xorg/xserver/tree/hw/kdrive/ephyr/README)
- [pulseaudio](https://www.freedesktop.org/wiki/Software/PulseAudio)

Note that xephyr/pulse are only needed for containers with desktop applications; CLI-only stuff can run without them. Also, as an Arch user, I track upstream versions pretty aggressively, so try the newest released versions of the above if you run into problems.

Once you have those things, clone the repo and build the base image with `./base/build` (requires root, as all the scripts in the repo do). You'll get an ACI that you can `rkt run`. More to come.

## Why not flatpak?

I _like_ flatpak and what it's trying to do. We need better isolation and disposable chroot/VM tooling on the desktop. [Qubes](https://www.qubes-os.org/doc/dispvm/) takes this use case seriously and the rest of us are only just now catching on. The [sandbox configuration](http://docs.flatpak.org/en/latest/working-with-the-sandbox.html) is particularly innovative. Being able to expose X11 or sound with just a command-line argument is awesome. I'm not hugely interested in its distribution system or its DBus integration, but I accept that those things solve real problems (using DBus for choosing files on the host is also innovative), and I'm fine with them if flatpak solves my problems. But it doesn't quite solve them yet.

The main issue for me is build tooling. There's no documentation for making new runtimes (ie base images). I have found documentation floating around on the internet, and my conclusion is that it's significantly more cumbersome than making base images with Docker/acbuild (where you basically put a rootfs into a tarball and call it a day). Being unable to modify rootfs directories (eg `/usr`) during application building is also a deal-breaker. Some applications (especially video games) have large or or unusual dependency trees, and I shouldn't have to put every imaginable lib into my base image just to make sure that other images can run on top of it.

[bubblewrap](https://github.com/projectatomic/bubblewrap) can be used independently of flatpak. I also really like bubblewrap and I was considering it instead of rkt. There's no good UX reason for containerization to require root (there are technical reasons, of course). But it's not feature-competitive with rkt and other server runtimes. I have to set up the rootfs somewhere on disk before I can execute into it with bubblewrap, and unpacking the rootfs would require superuser privileges, which defeats the main appeal of using bubblewrap at all (for me). (I am aware of userns-based tools like [vagga](https://github.com/tailhook/vagga), which are also unprivileged, but I'm too lazy to patch my kernel to support them. See Arch maintainers' thoughts on userns [here](https://bugs.archlinux.org/task/36969). You may also be interested in the [rootless containers](https://rootlesscontaine.rs/) page maintained by cyphar. Most of the work discussed there also depends on userns.)

Basically, my criticism is that the tools are immature when compared to what server tools can do (which is to be expected, of course). I expect that they will become more mature in the future, and rktscience will become obsolete, but we're not there yet.
