module.exports = {
    apps: [
      {
        name: 'DashAutumnApp',
        script: 'cd src/autumnAppChallenge && /root/miniconda3/envs/dash-autumn-app/bin/gunicorn -w 4 -b 0.0.0.0:8090 app:server',
        instances: 1,
        autorestart: true,
        watch: true,
        env: {
          NODE_ENV: 'production',
        },
      },
    ],
  };