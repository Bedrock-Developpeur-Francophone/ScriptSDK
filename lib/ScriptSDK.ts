import { ChatSendAfterEvent, InvalidContainerSlotError, PlayerBreakBlockAfterEvent, system, world } from "@minecraft/server";
import ScriptSDK from "./src/sdk";
import { NotFoundException } from "./src/exceptions";
import { Player } from '@minecraft/server';
import { BossBarColor, BossBarStyle } from "./src/enums";
import caches from "./src/caches";
import { Group } from "./src/groups";

export const prefix = "[ScriptSDK] ";

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
         * Defines the target player name for the player.
         */
        setNameTagForPlayer(target: Player, newName: string): Promise<void>;

        /**
         * Get the name of the player visible to the targeted player.
         */
        getNameTagByPlayer(target: Player): string;

        /**
         * Reset the name of the player visible to the targeted player.
         */
        resetNameTagForPlayer(target: Player): Promise<void>;

        /**
         * List of groups where the player is located.
         */
        groups: Group[];

        /**
         * Get the player's ping
         */
        getPing(): Promise<number>;
    }
}

function loadPlayer(player: Player) {
    ScriptSDK.send('getPlayerIp', [player.name]).then((result) => {
        if (result.success) {
            player.ip = result.result;
        }else{
            if (result.code == 404) throw new NotFoundException(prefix+result?.result);
            throw new Error(prefix+result?.result);
        }
    });

    ScriptSDK.send('getPlayerXuid', [player.name]).then((result) => {
        if (result.success) {
            player.xuid = result.result;
        }else{
            if (result.code == 404) throw new NotFoundException(prefix+result?.result);
            throw new Error(prefix+result?.result);
        }
    });

    ScriptSDK.send('getPlayerOS', [player.name]).then((result) => {
        if (result.success) {
            player.device_os = result.result;
        }else{
            if (result.code == 404) throw new NotFoundException(prefix+result?.result);
            throw new Error(prefix+result?.result);
        }
    });

    player.setBossBar = async (title, color, style, percent) => {
        const result = await ScriptSDK.send('setBossBar', [title, `${color}`, `${style}`, `${percent}`, `${player.name}`]);
        if (!result?.success) {
            if (result?.code == 404) throw new NotFoundException(prefix+result?.result);
            throw new Error(prefix+result?.result);
        }
    }

    if (!caches.nameTagCache[player.name]) {
        caches.nameTagCache[player.name] = {}
    }
    player.setNameTagForPlayer = async (target, newName) => {
        caches.nameTagCache[player.name][target.name] = newName;
        const result = await ScriptSDK.send('setPlayerNameForPlayer', [target.name, player.name, newName]);
        if (!result?.success) {
            if (result?.code == 404) throw new NotFoundException(prefix+result?.result);
            throw new Error(prefix+result?.result);
        }
    }

    player.getNameTagByPlayer = (target) => {
        return caches.nameTagCache[player.name][target.name];
    }

    player.resetNameTagForPlayer = async (target) => {
        if (Object.keys(caches.nameTagCache[player.name]).includes(target.name)) {
            delete caches.nameTagCache[player.name][target.name];
            
            const result = await ScriptSDK.send('resetPlayerNameForPlayer', [target.name, player.name]);
            if (!result?.success) {
                if (result?.code == 404) throw new NotFoundException(prefix+result?.result);
                throw new Error(prefix+result?.result);
            }
        }
    }

    player.groups = [];

    player.getPing = async () => {
        const result = await ScriptSDK.send('getPlayerPing', [player.name]);
        if (!result?.success) {
            if (result?.code == 404) throw new NotFoundException(prefix+result?.result);
            throw new Error(prefix+result?.result);
        }
        return parseInt(result.result);
    }
}

world.afterEvents.playerSpawn.subscribe(async (e) => {
    const player = e.player;
    loadPlayer(player);
});

world.afterEvents.worldLoad.subscribe(async () => {
    world.getAllPlayers().forEach((p) => {
        loadPlayer(p);
    });
});