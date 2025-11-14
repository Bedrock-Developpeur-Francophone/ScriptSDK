import { ScriptEventCommandMessageAfterEvent, system, world } from "@minecraft/server";

export type WaitingData = {
    [key: string]: (result: any) => void;
}

export type actions = 'getIp';

export class NotFoundException extends Error {
    constructor(msg: string) {
        super(msg);
        this.name = 'NotFoundException';
    }
}

class ScriptSDK {

    private waitingData: WaitingData = {};

    constructor() {
        system.afterEvents.scriptEventReceive.subscribe((e) => this.event(e))
    }

    private generateId(length = 10): string {
        var result = '';
        var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        var charactersLength = characters.length;
        for (var i = 0; i < length; i++) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    }

    private event(e: ScriptEventCommandMessageAfterEvent) {
        const { id, message, sourceEntity, sourceType } = e;

        const [message_type, message_id] = id.split(':');

        if (message_type == 'scriptsdkresult') {
            if (Object.keys(this.waitingData).includes(message_id)) {
                this.waitingData[message_id](message);
                delete this.waitingData[message_id];
            }
        }
    }

    private async send(action: actions, body: string = '', hasResult: boolean = false) : Promise<{success: boolean, code: number, result: string} | null> {
        return new Promise((resolve) => {

            const id = this.generateId();

            world.getDimension('overworld').runCommand(`scriptevent scriptsdk:${id}-${action} ${body}`);

            if (!hasResult) {
                resolve(null);
            }

            this.waitingData[id] = (data : string) => {
                const regex = /^([a-z]*)#(\d{3})#(.*)$/gm; // You're not good at regular expressions, go to -> https://regex101.com/ ;D
                let m = regex.exec(data);
                if(m && m.length == 3) {
                    resolve({
                        success: m[0] == 'true',
                        code: parseInt(m[1]),
                        result: m[2]
                    });
                }
            }
        });
    }

    /**
     * Return player ip.
     */
    async getIp(playerName: string) {
        const result = await this.send('getIp', playerName, true);
        if(result?.success) {
            return result.result;
        }
        if(result?.code == 404) throw new NotFoundException(result?.result);
        throw new Error(result?.result);
    }
}

export default new ScriptSDK();