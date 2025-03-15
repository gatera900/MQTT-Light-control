import paho.mqtt.client as mqtt
import json
from datetime import datetime

# MQTT Configuration
MQTT_BROKER = "157.173.101.159"
MQTT_PORT = 9001
MQTT_TOPIC_CONTROL = "/student_group/light_control"
MQTT_TOPIC_STATUS = "/student_group/light_status"

light_state = {
    "status": "OFF",
    "last_updated": None
}

def update_light_state(status=None):
    """Update light state and publish to status topic"""
    global light_state
    
    if status is not None:
        light_state["status"] = status
    
    light_state["last_updated"] = datetime.now().isoformat()
    
    client.publish(MQTT_TOPIC_STATUS, json.dumps(light_state))

    status_emoji = "\U0001F4A1" if light_state["status"] == "ON" else "⚫"
    print(f"\n{status_emoji} Light Status: {light_state['status']}")

def on_connect(client, userdata, flags, rc):
    """Callback when client connects to the broker"""
    if rc == 0:
        print("✅ Connected to MQTT broker successfully")
        client.subscribe(MQTT_TOPIC_CONTROL)
        print(f"📡 Subscribed to topic: {MQTT_TOPIC_CONTROL}")
        
        update_light_state()
    else:
        print(f"❌ Failed to connect to MQTT broker with code: {rc}")

def on_message(client, userdata, msg):
    """Callback when a message is received from the broker"""
    try:
        topic = msg.topic
        payload = msg.payload.decode()
        
        if topic == MQTT_TOPIC_CONTROL:
            if payload in ["ON", "OFF"]:
                update_light_state(status=payload)
                
    except Exception as e:
        print(f"❌ Error processing message: {e}")

def print_menu():
    """Print the control menu"""
    print("\n🎮 Light Control Options:")
    print("1. Turn ON")
    print("2. Turn OFF")
    print("3. Show Current State")
    print("4. Exit")
    return input("Enter your choice (1-4): ")

def main():
    global client
    
    client = mqtt.Client(transport="websockets")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print(f"🔄 Connecting to broker: {MQTT_BROKER}")
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_start()

        while True:
            choice = print_menu()

            if choice == "1":
                update_light_state(status="ON")
            
            elif choice == "2":
                update_light_state(status="OFF")
            
            elif choice == "3":
                print("\n📊 Current Light State:")
                print(f"Status: {light_state['status']}")
                print(f"Last Updated: {light_state['last_updated']}")
            
            elif choice == "4":
                print("👋 Exiting...")
                break
            
            else:
                print("⚠️ Invalid choice. Please try again.")

    except KeyboardInterrupt:
        print("\n👋 Program terminated by user")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("📡 Disconnected from MQTT broker")

if __name__ == "__main__":
    main()
