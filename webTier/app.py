import threading
from webTier import app
from webTier.service import appScalingService

appScalingService = appScalingService.AppScalingService()
autoScaleUp = threading.Thread(target=appScalingService.scaleServiceUp)
autoScaleUp.start()
autoScaleDown = threading.Thread(target=appScalingService.scaleServiceDown)
autoScaleDown.start()
if __name__ == '__main__':
    app.run()
