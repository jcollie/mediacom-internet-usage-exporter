# Mediacom Internet Usage Exporter

An exporter for [Prometheus](https://prometheus.io/) to keep track of
your Internet usage, if your Internet provider is [Mediacom
Communications](https://www.mediacomcable.com/).

To use this exporter, you'll need (in addition to being a customer of Mediacom Communications):

* Your Mediacom customer ID.
* The URL to the Mediacom usage report generator

### Getting your Mediacom customer ID

Your Mediacom customer ID can be found by logging into your [Mediacom
account
dashboard](https://support.mediacomcable.com/#!/Account/Dashboard).

### Getting the Report URL

The URL to the Mediacom usage report generator can be found by going
to the [Mediacom usage
meter](http://mediacomtoday.com/usagemeter/index.php) and getting the
URL of the central iframe. In Firefox, you can right click in the
center of the window, select "This Frame -> View Frame Info" from the
pop-up menu. The report url will be the "Address:" entry in the "Frame
Info" window that pops up.

## Docker

Build container and push to local registry:

```
sudo docker build -t registry/mediacom-internet-usage-exporter:1 .
sudo docker push registry/mediacom-internet-usage-exporter:1
```

## Kubernetes


```
apiVersion: apps/v1beta1
kind: Deployment
metadata:
  name: mediacom-internet-usage-exporter
spec:
  replicas: 1
  template:
    metadata:
      labels:
        k8s-app: mediacom-internet-usage-exporter
    spec:
      containers:
        - name: mediacom-internet-usage-exporter
          image: registry/mediacom-internet-usage-exporter:1
          env:
            - name: "CUSTOMER_ID"
	      value: "XXXXXXXXXXXXXXXX"
            - name: "REPORT_URL"
	      value: "http://XX.XX.XX.XX/um/usage.action"
          ports:
            - name: metrics
              containerPort: 9336
              protocol: TCP
          resources:
            limits:
              cpu: "250m"
              memory: "256Mi"
```

## Prometheus


```
  - job_name: 'mediacom-internet-usage'
    scrape_interval: 5m
    scrape_timeout: 60s
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels:
          - __meta_kubernetes_pod_label_k8s_app
        regex: mediacom-internet-usage-exporter
        action: keep
      - source_labels:
          - __meta_kubernetes_namespace
        regex: default
        action: keep
      - source_labels:
          - __meta_kubernetes_pod_container_port_name
        regex: metrics
        action: keep
```
