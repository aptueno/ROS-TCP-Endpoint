#  Copyright 2020 Unity Technologies
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import rclpy
import re

from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy, QoSHistoryPolicy
from rclpy.serialization import deserialize_message

from .communication import RosSender


def get_qos_profile_for_topic(topic: str, default_depth=100) -> QoSProfile:
    """
    Return an appropriate QoS profile based on the topic name.
    This allows special handling of topics like /tf_static.
    """
    if topic.endswith("/tf_static"):
        return QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=default_depth,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL
        )
    else:
        return QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=default_depth,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE
        )


class RosPublisher(RosSender):
    """
    Class to publish messages to a ROS topic
    """

    def __init__(self, topic, message_class, queue_size=100, latch=False):
        """
        Args:
            topic:         Topic name to publish messages to
            message_class: The message class in catkin workspace
            queue_size:    Max number of entries to maintain in an outgoing queue
            latch:         Not used in ROS 2 (included for compatibility)
        """
        strippedTopic = re.sub("[^A-Za-z0-9_]+", "", topic)
        node_name = f"{strippedTopic}_RosPublisher"
        RosSender.__init__(self, node_name)

        self.msg = message_class()
        qos_profile = get_qos_profile_for_topic(topic, default_depth=queue_size)
        self.pub = self.create_publisher(message_class, topic, qos_profile)

    def send(self, data):
        """
        Takes in serialized message data from source outside of the ROS network,
        deserializes it into it's message class, and publishes the message to ROS topic.

        Args:
            data: The already serialized message_class data coming from outside of ROS
        """
        self.pub.publish(data)
        return None

    def unregister(self):
        """

        Returns:

        """
        self.destroy_publisher(self.pub)
        self.destroy_node()
