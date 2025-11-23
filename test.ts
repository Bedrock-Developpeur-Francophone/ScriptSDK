import './lib/ScriptSDK';
import { world } from '@minecraft/server';

world.beforeEvents.chatSend.subscribe((e) => {
    const player = e.sender;

    world.sendMessage(`Device : ${player.device_os}`);
});

// I use this file to test lib.