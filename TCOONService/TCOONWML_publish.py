from ZSI.ServiceContainer import AsServer
from TCOONWMLImp import WaterOneFlowServiceImpl
from ZSI import dispatch
from datetime import datetime

if __name__ == "__main__":
    print "Starting TCOON WaterML Server...."
    port = 9080
    AsServer(port,(WaterOneFlowServiceImpl('TCOONWaterML'),))