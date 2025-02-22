app_deployment = """
apiVersion : "apps/v1"
kind: Deployment
metadata:
  name: pumpwood-description-matcher-app
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      type: app
      endpoint: pumpwood-description-matcher-app
      function: description-matcher
  template:
    metadata:
      labels:
        type: app
        endpoint: pumpwood-description-matcher-app
        function: description-matcher
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: bucket-key
        secret:
          secretName: bucket-key
      containers:
      - name: pumpwood-description-matcher
        image: {repository}/pumpwood-description-matcher-app:{version}
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
            path: /health-check/pumpwood-description-matcher-app/
            port: 5000
        env:
        - name: DEBUG
          value: "{debug}"

        # HASH_SALT
        - name: HASH_SALT
          valueFrom:
            secretKeyRef:
              name: hash-salt
              key: hash_salt

        # Database
        - name: DB_HOST
          value: "postgres-pumpwood-description-matcher"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: pumpwood-description-matcher
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
                name: pumpwood-description-matcher
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
  name: pumpwood-description-matcher-app
  labels:
    type: app
    endpoint: pumpwood-description-matcher-app
    function: description-matcher
spec:
  type: ClusterIP
  ports:
    - port: 5000
      targetPort: 5000
  selector:
    type: app
    endpoint: pumpwood-description-matcher-app
    function: description-matcher
"""

secrets = """
apiVersion: v1
kind: Secret
metadata:
  name: pumpwood-description-matcher
type: Opaque
data:
  db_password: {db_password}
  microservice_password: {microservice_password}
  ssl_key: {ssl_key}
  ssl_crt: {ssl_crt}
"""

services__load_balancer = """
apiVersion : "v1"
kind: Service
metadata:
  name: loadbalancer-postgres-pumpwood-description-matcher
  labels:
      type: loadbalancer-db
      endpoint: pumpwood-description-matcher-app
      function: description-matcher
spec:
  type: LoadBalancer
  ports:
    - port: 7000
      targetPort: 5432
  selector:
      type: db
      endpoint: pumpwood-description-matcher-app
      function: description-matcher
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
  name: {disk_name}
  labels:
    usage: {disk_name}
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
  name: postgres-pumpwood-description-matcher
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: {disk_size}
  volumeName: {disk_name}
"""


deployment_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-pumpwood-description-matcher
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: pumpwood-description-matcher-app
      function: description-matcher
  template:
    metadata:
      labels:
        type: db
        endpoint: pumpwood-description-matcher-app
        function: description-matcher
    spec:
      volumes:
      - name: pumpwood-description-matcher-data
        persistentVolumeClaim:
          claimName: postgres-pumpwood-description-matcher
      - name: postgres-init-configmap
        configMap:
          name: postgres-init-configmap
      - name: secrets
        secret:
          secretName: pumpwood-description-matcher
      - name: dshm
        emptyDir:
          medium: Memory
      containers:
      - name: postgres-pumpwood-description-matcher
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
              name: pumpwood-description-matcher
              key: db_password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata

        volumeMounts:
        - name: pumpwood-description-matcher-data
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
  name: postgres-pumpwood-description-matcher
  labels:
    type: db
    endpoint: pumpwood-description-matcher-app
    function: description-matcher
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: pumpwood-description-matcher-app
    function: description-matcher
"""

test_postgres = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-pumpwood-description-matcher
spec:
  replicas: 1
  selector:
    matchLabels:
      type: db
      endpoint: pumpwood-description-matcher-app
      function: description-matcher
  template:
    metadata:
      labels:
        type: db
        endpoint: pumpwood-description-matcher-app
        function: description-matcher
    spec:
      imagePullSecrets:
        - name: dockercfg
      volumes:
      - name: dshm
        emptyDir:
          medium: Memory
      containers:
      - name: postgres-pumpwood-description-matcher
        image: {repository}/test-db-description-matcher:{version}
        imagePullPolicy: Always
        resources:
          requests:
            cpu: "1m"
          limits:
            cpu: "3"
        volumeMounts:
        - name: dshm
          mountPath: /dev/shm
        ports:
        - containerPort: 5432
---
apiVersion : "v1"
kind: Service
metadata:
  name: postgres-pumpwood-description-matcher
  labels:
    type: db
    endpoint: pumpwood-description-matcher-app
    function: description-matcher
spec:
  type: ClusterIP
  ports:
    - port: 5432
      targetPort: 5432
  selector:
    type: db
    endpoint: pumpwood-description-matcher-app
    function: description-matcher
"""
