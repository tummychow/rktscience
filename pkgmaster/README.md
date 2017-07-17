# pkgmaster

pkgmaster is a tool for building PKGBUILDs inside a temporary environment. It's based on [makechrootpkg](https://git.archlinux.org/devtools.git/tree/makechrootpkg.in) from [devtools](https://www.archlinux.org/packages/extra/any/devtools/). Its basic functionality is similar, but this tool is based on ACIs, which means you don't have to juggle and update multiple chroots (mkarchroot was always the part that annoyed me about my old chroot-based pkgbuild workflow).

The PKGBUILD process I recommend is an entirely manual one (no yaourt or pacaur here). It works like this:

1. build the pkgmaster ACI:

    ```bash
    sudo base/build
    sudo pkgmaster/build <path to base ACI>
    ```

2. add a user repo to your `pacman.conf`:

    ```
    [user]
    Server = file:///var/lib/pkgmaster
    SigLevel = Optional TrustAll
    ```

3. get a PKGBUILD to build. If you want to download from the AUR, I recommend [cower](https://github.com/falconindy/cower).

4. invoke rkt to launch pkgmaster, binding the build and repo directories appropriately:

    ```bash
    sudo pkgmaster/run <path to pkgmaster ACI> <path to PKGBUILD folder> /var/lib/pkgmaster
    ```

5. you should have a package in the repo directory, and you can install it with pacman like anything else: `pacman -Syu <name of built package>`
