# Maintainer : swarnim.114@gmail.com
pkgname=webapp-creator
pkgver=1.0.0
pkgrel=1
pkgdesc="A simple CLI tool to create desktop web applications on Linux"
arch=('any')
url="https://github.com/Swarnim114/webapp-creator"
license=('MIT')
depends=('python')
source=("https://raw.githubusercontent.com/Swarnim114/webapp-creator/main/webapp_creator.py")
sha256sums=('SKIP')

package() {
    # Create the destination directory
    install -dm755 "$pkgdir/usr/bin"
    
    # Install the script to /usr/bin/webapp-creator and make it executable
    install -m755 "webapp_creator.py" "$pkgdir/usr/bin/webapp-creator"
}
