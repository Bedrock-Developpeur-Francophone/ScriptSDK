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
    
    private deserializer(message: string, args: number = 1) {
        const repeatedPattern = Array(args).fill("(.*)").join(';#;');
        const regex = new RegExp(`^([a-z]*);#;(\\d{3});#;${repeatedPattern}$`, 'gm');
        return regex.exec(message);
    }

    private getResultBody(result: string[], length: number) : string[] {
        const cleanResult = new Array(length);
        result.map((value, index) => {
            if(index > 2) {
                cleanResult[index - 3] = value;
            }
        });
        return cleanResult;
    }
    
    public async send(action: string, body: string[], args: number = 1): Promise<{ success: boolean, code: number, result: string[] }> {
        return new Promise((resolve) => {
            
            const id = this.generateId();

            system.sendScriptEvent(`scriptsdk:${id}-${action}`, `${body.join(';#;')}`);

            this.waitingData[id] = (data: string) => {
                let m = this.deserializer(data, args);
                if (m && m.length >= 4) {
                    resolve({
                        success: m[1] == 'true',
                        code: parseInt(m[2]),
                        result: m[1] == 'true' ? this.getResultBody(m, args) : [m[3]]
                    });
                }
            }
        });
    }
}

export default new ScriptSDK();