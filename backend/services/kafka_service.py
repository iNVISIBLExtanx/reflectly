"""
Kafka Service for Reflectly
Handles publishing and consuming messages from Kafka topics
"""
import json
import threading
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaService:
    def __init__(self, bootstrap_servers="kafka:9092"):
        """
        Initialize Kafka producer and consumer configurations
        
        Args:
            bootstrap_servers (str): Kafka bootstrap servers
        """
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumers = {}
        self.consumer_threads = {}
        
        # Initialize producer
        self._init_producer()
        
    def _init_producer(self):
        """Initialize Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            logger.info(f"Kafka producer initialized with bootstrap servers: {self.bootstrap_servers}")
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.producer = None
            
    def publish_message(self, topic, key, value):
        """
        Publish a message to a Kafka topic
        
        Args:
            topic (str): Kafka topic
            key (str): Message key
            value (dict): Message value
            
        Returns:
            bool: True if message was published successfully, False otherwise
        """
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return False
            
        try:
            future = self.producer.send(topic, key=key, value=value)
            self.producer.flush()
            record_metadata = future.get(timeout=10)
            logger.info(f"Message published to topic {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish message to topic {topic}: {e}")
            return False
            
    def consume_messages(self, topic, callback, group_id=None):
        """
        Consume messages from a Kafka topic and process them using the provided callback
        
        Args:
            topic (str): Kafka topic
            callback (function): Callback function to process messages
            group_id (str): Consumer group ID
            
        Returns:
            bool: True if consumer was started successfully, False otherwise
        """
        if topic in self.consumers:
            logger.warning(f"Consumer for topic {topic} already exists")
            return False
            
        try:
            # Create consumer
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id=group_id or f"reflectly-{topic}-consumer",
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            
            # Store consumer
            self.consumers[topic] = consumer
            
            # Start consumer thread
            thread = threading.Thread(target=self._consume_loop, args=(topic, callback))
            thread.daemon = True
            thread.start()
            
            # Store thread
            self.consumer_threads[topic] = thread
            
            logger.info(f"Started consumer for topic {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to start consumer for topic {topic}: {e}")
            return False
            
    def _consume_loop(self, topic, callback):
        """
        Consume messages in a loop
        
        Args:
            topic (str): Kafka topic
            callback (function): Callback function to process messages
        """
        consumer = self.consumers.get(topic)
        if not consumer:
            logger.error(f"Consumer for topic {topic} not found")
            return
            
        logger.info(f"Starting consume loop for topic {topic}")
        try:
            for message in consumer:
                try:
                    logger.info(f"Received message from topic {topic}: {message.value}")
                    callback(message.value)
                except Exception as e:
                    logger.error(f"Error processing message from topic {topic}: {e}")
        except Exception as e:
            logger.error(f"Error in consume loop for topic {topic}: {e}")
        finally:
            logger.info(f"Consume loop for topic {topic} ended")
            
    def stop_consumer(self, topic):
        """
        Stop a consumer for a topic
        
        Args:
            topic (str): Kafka topic
            
        Returns:
            bool: True if consumer was stopped successfully, False otherwise
        """
        if topic not in self.consumers:
            logger.warning(f"Consumer for topic {topic} not found")
            return False
            
        try:
            consumer = self.consumers.pop(topic)
            consumer.close()
            logger.info(f"Stopped consumer for topic {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop consumer for topic {topic}: {e}")
            return False
            
    def stop_all_consumers(self):
        """
        Stop all consumers
        
        Returns:
            bool: True if all consumers were stopped successfully, False otherwise
        """
        success = True
        for topic in list(self.consumers.keys()):
            if not self.stop_consumer(topic):
                success = False
        return success
