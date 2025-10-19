"""
Heartbeat receiving logic.
"""

from pymavlink import mavutil

from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatReceiver:
    """
    HeartbeatReceiver class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> "tuple[True, HeartbeatReceiver] | tuple[False, None]":
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """
        try:
            heartbeat_receiver = cls(cls.__private_key, connection, local_logger)
            return True, heartbeat_receiver
        except (OSError, mavutil.mavlink.MAVError) as exception:
            local_logger.error(f"Heartbeat Receiver object creation failed: {exception}")
            return False, None  #  Create a Heartbeat Receiver object

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        # Do any intializiation here
        self.connection = connection
        self.local_logger = local_logger
        self.missed_heartbeats = 0
        self.state = "DISCONNECTED"

    def run(
        self,
    ) -> str:
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        signal = self.connection.recv_match(type="HEARTBEAT", blocking=True, timeout=1.2)

        if signal and signal.get_type() == "HEARTBEAT":
            self.missed_heartbeats = 0 
            self.local_logger.info("CONNECTED. Heartbeat Received.", True)
            self.state = "CONNECTED"
        else:
            self.missed_heartbeats += 1  # If variable hits 5, receiver is no longer connected
            self.local_logger.warning("Missed Heartbeat!", True)
            if self.missed_heartbeats >= 5:
                self.state = "DISCONNECTED"
                self.local_logger.error("DISCONNECTED due to 5 or more missed heartbeats!", True)
            if self.missed_heartbeats < 5:
                self.local_logger.error("CONNECTED. Heartbeat missed.", True)
        return self.state


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
