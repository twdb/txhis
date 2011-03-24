from ZSI.ServiceContainer import AsServer
from CBIWMLImp import WaterOneFlowServiceImpl
from ZSI import dispatch
from datetime import datetime

if __name__ == "__main__":
    print "Starting CBI WaterML Server...."
    port = 9080
    AsServer(port,(WaterOneFlowServiceImpl('CBIWaterML'),))
