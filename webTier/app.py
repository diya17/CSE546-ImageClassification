import threading

from webTier import app
from webTier.service import appScalingService

autoScale = threading.Thread(appScalingService.scaleServiceUp())
autoScale.start()

if __name__ == '__main__':
    app.run()
