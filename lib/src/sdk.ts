import { ScriptEventCommandMessageAfterEvent, system, world } from "@minecraft/server";

export type WaitingData = {
    [key: string]: (result: any) => void;
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

    public async send(action: string, body: string[]): Promise<{ success: boolean, code: number, result: string }> {
        return new Promise((resolve) => {
            
            const id = this.generateId();

            world.getDimension('overworld').runCommand(`scriptevent scriptsdk:${id}-${action} ${body.join(';#;')}`);

            this.waitingData[id] = (data: string) => {
                const regex = /^([a-z]*);#;(\d{3});#;(.*)$/gm; // You're not good at regular expressions, go to -> https://regex101.com/ ;D
                let m = regex.exec(data);
                if (m && m.length == 4) {
                    resolve({
                        success: m[1] == 'true',
                        code: parseInt(m[2]),
                        result: m[3]
                    });
                }
            }
        });
    }
}

export default new ScriptSDK();