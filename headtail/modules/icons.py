# -*- coding: utf-8 -*-

import base64
import zlib

from PyQt5.QtGui import QPixmap


class Icons():
    def _decompressPixmap(self, data):
        icon_data = zlib.decompress(base64.b64decode(data))
        pixmap = QPixmap()
        pixmap.loadFromData(icon_data)
        return pixmap

    def pythonPixmap(self):
        return self._decompressPixmap(
            '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'
            'sFe4A=='
        )

    def bqhtViewerPixmap(self):
        return self._decompressPixmap(
            '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'
            'IJayZui'
        )

    def savePixmap(self):
        return self._decompressPixmap(
            'eNpz93SzsEwUYBBgeMbA8OPHn6jK1dFAVAUkV8VVr0qsXXnn8fs3779EV61KqFuZUr8ipWFFRtPy6Ztubj33afvJx7tOP9l37umRS89PX'
            'nt57tbr8yD06sOnrzmty3adebLp8O3dIPLWvvPP9p9/evjS88OXnp249vLktRfnb78+d+vV1ftvr95/c/vxu0cvPqQ3L89uXVbQsfQESP'
            'bV8zefzl++sfPo5dtP3j188eHZm8/F3UvKexe/+fAlonRied/imgmLHr39Xj1h0cO33998/nn7xaeHb7/VT1545+WnN59/fPj89fbLT68'
            '//2iauqB52oLPX7+1Tp/fNmN+x0wgmrf98LHC5rau2fM27t3fNXvOt58/v//8uXTzun9/fz05P/f///8MAwEUf7IwMjBEMOiAOKA4YWC/'
            '0xDR1NzS2mQQ0Okf2NPj3xlgEOHr6ekXNmNmmN9UnwgvCZeAkCUhwUsCFnpHeJhzBNhtdHbbGGBu7h7haKIfYLvf1trBIUBf3zHCRtM4w'
            'NXe1cneyTXA2NgqwszIKCD83v3wAHYNywhTNXXZCa+l1dVMI3T0xMT0xFW/fBFVUdWJkFTWYElxmPCgQ0zJbc2BSwlOHAI8DB4sBa2MHd'
            '1aG3QmKDxkZmZXWOqR+OFgMwtbBI9Lx4LGg83TQ1cZRJx0ZJzGJFBk9KNtcZIfB+uGIxIOCo0MjCxMHB4TGg4EMTUyMFgDAJ92FrQ='
        )

    def deletePixmap(self):
        return self._decompressPixmap(
            'eNpz93SzsEwUYBBguMrAcNzY9EthyZfiks9FJZ+LS29o6T/QMbmvY3xc0+CZmd1TM7ujCtpPDSw/hSZ8Sc7+nJz1GUimZB+VUD8mqXFUU'
            'v2Ygs6nkISjwqof7YM+2Ad+8oj46BFxJbXk/pwVp2I9z+XFnQp3OxXhdjLC7WpHzckA5zvLFpx0tzvpbn/C3f64reWDxOivjbXHba0eB/'
            'l/baj70lD3+MiR////MxANFH+yMDIwGDLogDggPzGw1RyYUeChI9XvPiM9RKYywSVihWgSl/siMQ4tnYkx2peWf1Hce0j1EYerwAqfVY4'
            'PUlSLIgRPHP7oUTiBgYuXV4yTwcOQg0daSoqHw0NGVGLKFO56VxnhKaxCrBKSIjOcZMUXiMvIyiyTFJd1NhBnW+G8ml08xmnjYqfVOzsO'
            'HDR0ZLAGAJ9seXs='
        )

    def timberClockPixmap(self):
        return self._decompressPixmap(
            'eNpz93SzsEwUYBBiOMTMAARnzpx59uzZf1Sg+JOFkYuBhUEHpAKkloE51GMXy4EJjYJxUw4/vf3sx3zmyqYHUxy3+qhOWMaQtdExk3vrq'
            'WPbX4ZvkctvuLwjZ3kQ2w6XTyzevOuuKhvVRqRsTHzruP2OmIZy9NIomxsnvjZFKvX9iJ7IwGANANvnQno='
        )

    def timberQueryPixmap(self):
        return self._decompressPixmap(
            'eNpz93SzsEwUYBBguMrAoNDgqAZEHY6OE8PjZuVbdfgbd3ikrS3X7XD0mBjuMSvcaqKH40T/tLVAKUfjcivHDg+Pif7+s8LDl8TpNhgbd'
            '1g5zvLwmOVvBWRMdAxfEu7R4JG2JK18bfna02t3Xdp19cHVuFnhHdsb8pfENazN79hePutgR8f2/Inbyyduz19ysKPhjNqhlxX/wYCBdK'
            'D4k4WRgUGPQQfEAfmJgW2Gw/QCDx0xx3YnhQCLhp51zYlbjVa6zEn7OEFjbdTqEK5WL5k2BeaXXzIb/T9Mfig5tcct9/urOvvdPIqNlVW'
            'NsmxObNJdcnm9OtKyjE4M/FN7euWnsjA4MYrMn64rN19AeFIgj6DgdLlV4kLMdQocQpI9cnx8kuLCHCWB3MJycqISYlLC3HXO7Bxcwry8'
            'wlwcp108mLyZ/ALuujoyWAMAWTx2oQ=='
        )

    def timberTablePixmap(self):
        return self._decompressPixmap(
            'eJxz93SzsEwUYBBgeMbAsGLDgfj8noSCnqzKKQX1M3ccvLj36JXonM7YvO7YvK74gp6Ewt7kkgnJJf3p5ZOyq6fm18/Mr59R3DS7pHlOe'
            'du86q5Fdb1Ldxy8sOfolePn76RXTMqsmpJdM628fX4ZSHZhbc/ixgnLmiet6Ji2esehi9sPXth24PzeY1cOnb5x7Pyd/IYZdX1L2qevaZ'
            '60vHvWuiUbDizbdGjtjuO7jlzacejCnmNXDp6+sf/ktX0nru45dvnExbvHL9w5dv720XO3Vm49smHP6a0Hzm0/dOHwuduHztw4duHOQRB'
            '5e8KCDf/BgGEoAMWfLIwMDB4MOiAOKE4Y2Oc1eDQ1t7S2tbeys3Mw8fLxCwjJimorKjW5OTs7Mpgb2dsZ2hroT/fo4uTmlZIRFBaRF5vW'
            'pOe+zXLbzp16TTpWVtbOkpquzlaSVs7KTbo7bXbt0m1S0HDR0DDVcLp+01ShSW6n2YWdIk0sJiZs6iYWEhLqbCYSWk3MO42ebJNu4nFQd'
            'WiImRGYdKyVSaXBREBEYTpnrbsIR5DLxkWuLhLMjAzWAB1mwTU='
        )
