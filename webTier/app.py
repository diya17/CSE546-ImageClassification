import threading
from webTier import app
from webTier.service import appScalingService

if __name__ == '__main__':
    appScalingService = appScalingService.AppScalingService()
    autoScale = threading.Thread(appScalingService.scaleServiceUp())
    autoScale.start()
    app.run()
