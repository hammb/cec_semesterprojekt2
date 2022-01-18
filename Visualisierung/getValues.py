from azure.cosmos import CosmosClient
import masurevalues
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time


def initialize(endpoint, key, database_name, container_name):
    # <create_cosmos_client>
    client = CosmosClient(endpoint, key)
    # <get_database_client>
    database = client.get_database_client(database_name)
    # <get_container_client>
    container = database.get_container_client(container_name)

    print("initialized client, database and container")
    print(client, database, container)
    return client, database, container

def setRandomValues(container):
    # only for testing
    print("writing data to container...")
    for i in range(100):
        # Add items to the container
        # masurevalues.get_random_Values() gives .json file with random values
        measure_item= masurevalues.get_random_Values(i)
        print(measure_item)
        # <create_item>
        container.create_item(body=measure_item)
        # </create_item>
        time.sleep(2)
    print("send random Values to Cosmos db container: ", container)
   
def getValues_from_container(container, num = 50, sensor_name=None):
    # Query these items using the SQL query syntax. 
    # Specifying the partition key value in the query allows Cosmos DB to retrieve data only from the relevant partitions, which improves performance
    # <query_items>
    query = "SELECT * FROM c"
    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True,
        max_item_count=num
    ))
    request_charge = container.client_connection.last_response_headers['x-ms-request-charge']
    print('Query returned {0} items. Operation consumed {1} request units'.format(len(items), request_charge))
    # nur die neuesten Werte bearbeiten
    items = items[-num:]
    # print("item from cosmosDB: ", items[-1])

    sensorValues={}
    sensors = ['sensor1', 'sensor2', 'sensor3']
    names=['messageId','temperature', 'humidity', 'wb','timestamp']
    for sensor in sensors:
        sensorValues[sensor]={}
        for n in names:
            sensorValues[sensor][n]=[]
    for item in items:
        for name in names:
            sensorValues[item['deviceId']][name].append(item[name])
    print('Sensor1: Temperaturwerte: ', sensorValues[sensor_name]["temperature"])
    print('Sensor1: Feutigkeitswerte: ', sensorValues[sensor_name]["humidity"])
    if name:
        # nur Werte des angefragten Sensors zurückgeben
        return sensorValues[sensor_name], sensor_name
    return sensorValues

def visualize(container, getValues):
    # Create figure for plotting
    fig, ax1 = plt.subplots(figsize=(13,5))
    ax2 = ax1.twinx()
    temp_s = []
    humid_s = []
    time_s = []

    def animate(i, temp_s, humid_s, time_s):
        values, title = getValues(container, sensor_name='sensor1')
        print(values)
        temp_s = values["temperature"]
        humid_s = values["humidity"]
        time_s = values["timestamp"]

        # Draw x and y lists
        ax1.clear()
        ax2.clear()
        ax1.plot(time_s, temp_s, label="temperature", color="orange")
        ax2.plot(time_s, humid_s, label="humidity", color="blue")

        ax1.set_xlabel("Zeit")
        ax1.set_ylabel("temperatur")
        ax2.set_ylabel("humidity")
        fig.autofmt_xdate() # setzt Uhrzeit auf x-achse schräg
        ax1.set_title(title)
        fig.legend(loc='lower right')
    ani = animation.FuncAnimation(fig, animate, fargs=(temp_s, humid_s, time_s),interval=1000)
    plt.show()
    print('end visualization')

def main():
    # Initialize the Cosmos client
    # our Cosmos DB
    endpoint = 'https://cectesthttpexsample.documents.azure.com:443'
    key = '1jEbFBUhKhPFi1eck3FNczVuxGsbX3x7BD6WtLAZF0M1KjdDS8UlvayvkXji907Fk54ekOFGDgLgCFBmWBbgWQ=='
    database_name='my-database' 
    container_name= 'my-container'

    client, database, container, = initialize(endpoint, key, database_name, container_name)
    # setRandomValues(container)
    # name = 'sensorValues2'
    # values = getValues_from_container(container, sensor_name='sensor1')
    values = getValues_from_container
    visualize(container, values)

if __name__ == '__main__':
    main()