import { ChatSendAfterEvent, Entity, InvalidContainerSlotError, PlayerBreakBlockAfterEvent, system, world } from "@minecraft/server";
import ScriptSDK from "./src/sdk";
import { NotFoundException } from "./src/exceptions";
import { Player } from '@minecraft/server';
import { BossBarColor, BossBarStyle } from "./src/enums";
import caches from "./src/caches";
import { Group } from "./src/groups";

export const prefix = "[ScriptSDK] ";

export type ServerInfo = {
    ping: number;
    edition: string;
    gameMode: string;
    mapName: string;
    name: string;
    players: {
        online: number;
        max: number;
    }
    serverId: number;
    version: string;
}

declare module '@minecraft/server' {
    interface Player {

        ip: string | null;
        xuid: string | null;
        device_os: string | null;

        /**
         *  Assigns a boss bar to a player.
         */
        setBossBar(title: string, color: BossBarColor, style: BossBarStyle, percent: number): Promise<void>;

        /**
         * Reset a boss bar to a player.
         */
        resetBossBar(): Promise<void>;

        /**
         * Get the player's ping
         */
        getPing(): Promise<number>;

        /**
         * Send toast notification. 
         */
        sendToast(title: string, content: string): Promise<void>;

        /**
         * Send popup. 
         */
        sendPopup(message: string): Promise<void>;
    }

    interface Entity {
        /**
         * Defines the target entity name for the player.
         */
        setNameTagForPlayer(target: Player, newName: string): Promise<void>;
        
        /**
         * Get the name of the entity visible to the targeted player.
         */
        getNameTagByPlayer(target: Player): string;

        /**
         * Reset the name of the entity visible to the targeted player.
         */
        resetNameTagForPlayer(target: Player): Promise<void>;
    }

    interface System {
        groups: Group[];

        /**
         *  
         */
        getInfoFromExternalServer(host: string, port: number): Promise<ServerInfo>;
    }
}

system.groups = [];
system.getInfoFromExternalServer = async (host, port) => {
    const result = await ScriptSDK.send('getExternalServerInfo', [host, `${port}`], 9);
    if (result.success) {
        const data = result.result;
        return {
            ping: parseInt(data[0]),
            edition: data[1],
            gameMode: data[2],
            mapName: data[3],
            name: data[4],
            players: {
                online: parseInt(data[5]),
                max: parseInt(data[6]),
            },
            serverId: parseInt(data[7]),
            version: data[8]
        }
    } else {
        throw new Error(prefix + result?.result[0]);
    }

}

function loadPlayer(player: Player) {
    ScriptSDK.send('getPlayerIp', [player.name]).then((result) => {
        if (result.success) {
            player.ip = result.result[0];
        } else {
            if (result.code == 404) throw new NotFoundException(prefix + result?.result[0]);
            throw new Error(prefix + result?.result[0]);
        }
    });

    ScriptSDK.send('getPlayerXuid', [player.name]).then((result) => {
        if (result.success) {
            player.xuid = result.result[0];
        } else {
            if (result.code == 404) throw new NotFoundException(prefix + result?.result[0]);
            throw new Error(prefix + result?.result[0]);
        }
    });

    ScriptSDK.send('getPlayerOS', [player.name]).then((result) => {
        if (result.success) {
            player.device_os = result.result[0];
        } else {
            if (result.code == 404) throw new NotFoundException(prefix + result?.result[0]);
            throw new Error(prefix + result?.result[0]);
        }
    });

    player.setBossBar = async (title, color, style, percent) => {
        const result = await ScriptSDK.send('setBossBar', [title, `${color}`, `${style}`, `${percent}`, `${player.name}`]);
        if (!result?.success) {
            if (result?.code == 404) throw new NotFoundException(prefix + result?.result[0]);
            throw new Error(prefix + result?.result[0]);
        }
    }

    player.resetBossBar = async () => {
        const result = await ScriptSDK.send('resetBossBar', [`${player.name}`]);
        if (!result?.success) {
            if (result?.code == 404) throw new NotFoundException(prefix + result?.result[0]);
            throw new Error(prefix + result?.result[0]);
        }
    }

    player.getPing = async () => {
        const result = await ScriptSDK.send('getPlayerPing', [player.name]);
        if (!result?.success) {
            if (result?.code == 404) throw new NotFoundException(prefix + result?.result[0]);
            throw new Error(prefix + result?.result[0]);
        }
        return parseInt(result.result[0]);
    }

    player.sendToast = async (title, content) => {
        const result = await ScriptSDK.send('sendToast', [player.name, title, content]);
        if (!result?.success) {
            if (result?.code == 404) throw new NotFoundException(prefix + result?.result[0]);
            throw new Error(prefix + result?.result[0]);
        }
    }

    player.sendPopup = async (message) => {
        const result = await ScriptSDK.send('sendPopup', [player.name, message]);
        if (!result?.success) {
            if (result?.code == 404) throw new NotFoundException(prefix + result?.result[0]);
            throw new Error(prefix + result?.result[0]);
        }
    }
}

function loadEntity(entity : Entity) {
    if (!caches.nameTagCache[entity.id]) {
        caches.nameTagCache[entity.id] = {}
    }
    entity.setNameTagForPlayer = async (target, newName) => {
        caches.nameTagCache[entity.id][target.name] = newName;
        const result = await ScriptSDK.send('setEntityNameForPlayer', [target.name, entity.id, newName]);
        if (!result?.success) {
            if (result?.code == 404) throw new NotFoundException(prefix + result?.result[0]);
            throw new Error(prefix + result?.result[0]);
        }
    }

    entity.getNameTagByPlayer = (target) => {
        return caches.nameTagCache[entity.id][target.name];
    }

    entity.resetNameTagForPlayer = async (target) => {
        if (Object.keys(caches.nameTagCache[entity.id]).includes(target.name)) {
            delete caches.nameTagCache[entity.id][target.name];

            const result = await ScriptSDK.send('resetEntityNameForPlayer', [target.name, entity.id, entity.nameTag]);
            if (!result?.success) {
                if (result?.code == 404) throw new NotFoundException(prefix + result?.result[0]);
                throw new Error(prefix + result?.result[0]);
            }
        }
    }
}

world.afterEvents.playerSpawn.subscribe(async (e) => {
    loadPlayer(e.player);
    loadEntity(e.player);
});

world.afterEvents.entitySpawn.subscribe(async (e) => {
    loadEntity(e.entity);
});

world.afterEvents.worldLoad.subscribe(async () => {
    world.getAllPlayers().forEach((p) => {
        loadPlayer(p);
        loadEntity(p);
    });
    world.getDimension('overworld').getEntities().forEach((e) => loadEntity(e));
    world.getDimension('nether').getEntities().forEach((e) => loadEntity(e));
    world.getDimension('the_end').getEntities().forEach((e) => loadEntity(e));
});