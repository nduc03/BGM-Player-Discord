git pull
podman build -t dis-bgm:latest .
podman create --name dis-bgm --env-file .env dis-bgm:latest
podman generate systemd --name --restart-policy=always dis-bgm > ~/.config/systemd/user/dis-bgm.service
systemctl --user daemon-reload
systemctl --user enable dis-bgm
systemctl --user start dis-bgm