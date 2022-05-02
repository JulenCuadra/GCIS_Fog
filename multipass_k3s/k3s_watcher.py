from kubernetes import client, config, watch
import datetime 


config.load_kube_config()

api = client.CoreV1Api()
watcher = watch.Watch()
#for event in watcher.stream(api.list_event_for_all_namespaces):
for event in watcher.stream(api.list_namespaced_event, "default"):
    now = datetime.datetime.now()
    now_ms = now.timestamp()
    print("%s %s %s %s" % (now, now_ms,
                           event['object'].metadata.name,
                           event['object'].message))

    