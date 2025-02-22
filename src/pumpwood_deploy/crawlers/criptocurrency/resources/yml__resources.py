app_deployment = """
apiVersion : "apps/v1"
kind: Deployment
metadata:
  name: crawler-criptocurrency-app
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      type: app
      endpoint: crawler-criptocurrency-app
      function: crawler
      data: criptocurrency
  template:
    metadata:
      labels:
          type: app
          endpoint: crawler-criptocurrency-app
          function: crawler
          data: criptocurrency
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: crawler-criptocurrency
        image: {repository}/crawler-criptocurrency-app:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: bucket-key
            readOnly: true
            mountPath: /etc/secrets
        readinessProbe:
          httpGet:
            path: /health-check/crawler-criptocurrency-app/
            port: 5000
        env:
        - name: APP_DEBUG
          value: "False"

        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # Database
        - name: DB_HOST
          value: "postgres-crawler-criptocurrency"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: crawler-criptocurrency
              key: db_password

        # Google
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: "/etc/secrets/key-storage.json"
        - name: STORAGE_BUCKET_NAME
          value: {bucket_name}
        - name: STORAGE_TYPE
          value: 'google_bucket'

        # RABBITMQ ETL
        - name: RABBITMQ_HOST
          value: "rabbitmq-main"
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        # Microsservice
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: crawler-criptocurrency
                key: microservice_password

        # workers_timeout
        - name: WORKERS_TIMEOUT
          value: "{workers_timeout}"
        ports:
        - containerPort: 5000
---
apiVersion : "v1"
kind: Service
metadata:
  name: crawler-criptocurrency-app
  labels:
      type: app
      endpoint: crawler-criptocurrency-app
      function: crawler
      data: criptocurrency
spec:
  type: ClusterIP
  ports:
    - port: 5000
      targetPort: 5000
  selector:
      type: app
      endpoint: crawler-criptocurrency-app
      function: crawler
      data: criptocurrency
"""


worker_candle_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crawler-criptocurrency--worker-candle
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: crawler-criptocurrency-app
      function: worker-candle
  template:
    metadata:
      labels:
          type: worker
          endpoint: crawler-criptocurrency-app
          function: worker-candle
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: crawler-criptocurrency-worker
        image: {repository}/crawler-criptocurrency--worker-candle:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: bucket-key
            readOnly: true
            mountPath: /etc/secrets
        env:
        # HASH_SALT
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # RABBITMQ
        - name: RABBITMQ_HOST
          value: "rabbitmq-main"
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        # Microsservice
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: crawler-criptocurrency
                key: microservice_password
"""


worker_balance_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crawler-criptocurrency--worker-balance
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: crawler-criptocurrency-app
      function: worker-balance
  template:
    metadata:
      labels:
          type: worker
          endpoint: crawler-criptocurrency-app
          function: worker-balance
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: crawler-criptocurrency-worker
        image: {repository}/crawler-criptocurrency--worker-balance:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: bucket-key
            readOnly: true
            mountPath: /etc/secrets
        env:
        # HASH_SALT
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # RABBITMQ
        - name: RABBITMQ_HOST
          value: "rabbitmq-main"
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        # Microsservice
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: crawler-criptocurrency
                key: microservice_password

        # Bitfinex Keys
        - name: BITFINEX_API_KEY
          valueFrom:
              secretKeyRef:
                name: crawler-criptocurrency
                key: bitfinex_api_key
        - name: BITFINEX_API_SECRET
          valueFrom:
              secretKeyRef:
                name: crawler-criptocurrency
                key: bitfinex_api_secret
"""

worker_order_deployment = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crawler-criptocurrency--worker-order
spec:
  replicas: 1
  selector:
    matchLabels:
      type: worker
      endpoint: crawler-criptocurrency-app
      function: worker-order
  template:
    metadata:
      labels:
          type: worker
          endpoint: crawler-criptocurrency-app
          function: worker-order
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: crawler-criptocurrency-worker
        image: {repository}/crawler-criptocurrency--worker-order:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
        volumeMounts:
          - name: bucket-key
            readOnly: true
            mountPath: /etc/secrets
        env:
        # HASH_SALT
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # RABBITMQ
        - name: RABBITMQ_HOST
          value: "rabbitmq-main"
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-main-secrets
              key: password

        # Microsservice
        - name: MICROSERVICE_PASSWORD
          valueFrom:
              secretKeyRef:
                name: crawler-criptocurrency
                key: microservice_password

        # Bitfinex Keys
        - name: BITFINEX_API_KEY
          valueFrom:
              secretKeyRef:
                name: crawler-criptocurrency
                key: bitfinex_api_key
        - name: BITFINEX_API_SECRET
          valueFrom:
              secretKeyRef:
                name: crawler-criptocurrency
                key: bitfinex_api_secret
"""

secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: crawler-criptocurrency
type: Opaque
data:
  db_password: {db_password}
  microservice_password: {microservice_password}
  bitfinex_api_key: {bitfinex_api_key}
  bitfinex_api_secret: {bitfinex_api_secret}
  ssl_key: {ssl_key}
  ssl_crt: {ssl_crt}
"""

services__load_balancer = """
apiVersion : "v1"
kind: Service
metadata:
  name: loadbalancer-postgres-crawler-criptocurrency
  labels:
      type: loadbalancer-db
      endpoint: crawler-criptocurrency-app
      function: crawler
      data: criptocurrency
spec:
  type: LoadBalancer
  ports:
    - port: 7000
      targetPort: 5432
  selector:
      type: db
      endpoint: crawler-criptocurrency-app
      function: crawler
      data: criptocurrency
  loadBalancerIP: {{ postgres_public_ip }}
  loadBalancerSourceRanges:
    {%- for ip in firewall_ips %}
      - {{ip}}
    {%- endfor %}
"""

volume_postgres = """
kind: PersistentVolume
apiVersion: v1
metadata:
  name: postgres-crawler-criptocurrency
  labels:
    usage: postgres-crawler-criptocurrency
spec:
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: {disk_size}
  storageClassName: standard
  gcePersistentDisk:
    fsType: ext4
    pdName: {disk_name}
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: postgres-crawler-criptocurrency
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: {disk_size}
  volumeName: postgres-crawler-criptocurrency
"""


deployment_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-crawler-criptocurrency
spec:
  replicas: 1
  selector:
    matchLabels:
        type: db
        endpoint: crawler-criptocurrency-app
        function: crawler
        data: criptocurrency
  template:
    metadata:
      labels:
        type: db
        endpoint: crawler-criptocurrency-app
        function: crawler
        data: criptocurrency
    spec:
      volumes:
      - name: crawler-criptocurrency-data
        persistentVolumeClaim:
          claimName: postgres-crawler-criptocurrency
      - name: postgres-init-configmap
        configMap:
          name: postgres-init-configmap
      - name: secrets
        secret:
          secretName: crawler-criptocurrency
      - name: dshm
        emptyDir:
          medium: Memory
      containers:
      - name: postgres-crawler-criptocurrency
        image: timescale/timescaledb-postgis:1.7.3-pg12
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
          limits:
            cpu: "3"
        env:
        - name: POSTGRES_USER
          value: pumpwood
        - name: POSTGRES_DB
          value: pumpwood
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: crawler-criptocurrency
              key: db_password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata

        volumeMounts:
        - name: crawler-criptocurrency-data
          mountPath: /var/lib/postgresql/data/
        - name: postgres-init-configmap
          mountPath: /docker-entrypoint-initdb.d/
        - name: secrets
          mountPath: /etc/secrets
          readOnly: true
        - name: dshm
          mountPath: /dev/shm
        ports:
        - containerPort: 5432
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-crawler-criptocurrency
  labels:
    type: db
    endpoint: crawler-criptocurrency-app
    function: crawler
    data: criptocurrency
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: crawler-criptocurrency-app
    function: crawler
    data: criptocurrency
"""
