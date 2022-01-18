using IoTHubTrigger = Microsoft.Azure.WebJobs.EventHubTriggerAttribute;

using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Host;
using Microsoft.Azure.EventHubs;
using System.Text;
using System.Net.Http;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

namespace IoTHubTriggerTestFunction
{
    public static class Function1
    {
        private static HttpClient client = new HttpClient();

        [FunctionName("Function1")]
        public static async Task RunAsync([IoTHubTrigger("messages/events", Connection = "ConnectionString")]EventData message, ILogger log,
            [CosmosDB(databaseName: "my-database", collectionName: "my-container",
            ConnectionStringSetting = "CosmosDbConnectionString"
    )]IAsyncCollector<dynamic> documentsOut)
        {
            string json = Encoding.UTF8.GetString(message.Body.Array);
            log.LogInformation($"C# IoT Hub trigger function processed a message: {json}");

            dynamic data = JsonConvert.DeserializeObject(json);

            foreach (var deviceMessage in data["Messages"])
            {
                log.LogInformation($"deviceMessage: {deviceMessage}");

                int messageId = deviceMessage.messageId;
                string deviceId = deviceMessage.deviceId;
                float temperature = deviceMessage.temperature;
                float humidity = deviceMessage.humidity;
                string wb = deviceMessage.wb;
                string timestamp = deviceMessage.timestamp;

                if (!string.IsNullOrEmpty(deviceId))
                {
                    // Add a JSON document to the output container.
                    await documentsOut.AddAsync(new
                    {
                        // create a random ID
                        id = System.Guid.NewGuid().ToString(),
                        messageId = messageId,
                        deviceId = deviceId,
                        temperature = temperature,
                        humidity = humidity,
                        wb = wb,
                        timestamp = timestamp
                    });
                }
            }
        }
    }
}