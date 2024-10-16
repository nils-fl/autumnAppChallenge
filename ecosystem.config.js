module.exports = {
    apps: [
      {
        name: 'DashAutumnApp',
        script: '/miniconda3/envs/dash-autumn-app/bin/gunicorn -w 2 -b 0.0.0.0:8090 app:server',
        instances: 1,
        autorestart: true,
        watch: true,
        max_memory_restart: '4G',
        env: {
          NODE_ENV: 'production',
        },
      },
    ],
  };