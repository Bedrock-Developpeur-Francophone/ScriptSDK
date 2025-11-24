# ScriptSDK

[![License](https://img.shields.io/badge/License-GPL--2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.4.1-green.svg)](package.json)

Use certain Endstone features directly in your Bedrock add-ons through a JavaScript API. ScriptSDK bridges the gap between Minecraft Bedrock add-ons and Endstone plugin capabilities.

⚠️ **Plugin currently under development.**

## 📋 Overview

ScriptSDK is a dual-component system:
- **JavaScript/TypeScript SDK**: Import and use in your Bedrock add-ons
- **Endstone Plugin**: Python-based server plugin that enables the SDK functionality

## ✨ Features

- /debug : To enable/disable the plugin's communication logs.
- **system.groups** → `Group[]`: List of groups initialise

### 💫 Player Features

- **player.ip** → `string | null`: Player's IP address (automatically populated when player spawns)
- **player.xuid** → `string | null`: Player's Xbox User ID (automatically populated when player spawns)
- **player.device_os** → `string | null`: Player's device OS (automatically populated when player spawns)
- **player.getPing()** → `Promise<number>`: Get the player's current ping/latency in milliseconds
- **player.setBossBar(title, color, style, percent)** → `Promise<void>`: Create and assign a boss bar to a player with customizable progress percentage (0-100)
- **player.setNameTagForPlayer(target, newName)** → `Promise<void>`: Set custom player name visible to specific players
- **player.resetNameTagForPlayer(target)** → `Promise<void>`: Reset custom player name to default for a specific target player
- **player.getNameTagByPlayer(target)** → `string`: Get the custom name tag that a specific player sees for this player

### 🛡️ Group System

Create and manage player groups with custom rules:

```typescript
import { Group } from 'lib/ScriptSDK';
import { GroupRule } from 'lib/src/enums';

// Create a new group with a rule
const safeZone = new Group('SafeZone', GroupRule.NO_DAMAGE);

// Initialize the group (required before using it)
await safeZone.init();

// Add players to the group
await safeZone.addPlayer(player);

// Remove players from the group
await safeZone.removePlayer(player);

// Get all players in the group
const groupPlayers = safeZone.getPlayers();

// Destroy the group
await safeZone.destroy();
```

**Group Properties:**
- `name` → `string`: The name of the group
- `rule` → `GroupRule`: The rule applied to the group
- `is_created` → `boolean`: Whether the group was successfully created
- `is_destroy` → `boolean`: Whether the group has been destroyed

**Group Methods:**
- `init()` → `Promise<void>`: Initialize the group on the server (must be called before using the group)
- `addPlayer(player | playerName)` → `Promise<void>`: Add a player to the group
- `removePlayer(player | playerName)` → `Promise<void>`: Remove a player from the group
- `hasPlayer(player | playerName)` → `boolean` : Returns a boolean value indicating whether the player is in the group
- `getPlayers()` → `Player[]`: Get all players in the group
- `destroy()` → `Promise<void>`: Delete the group and remove all players from it
- `toJson()` → `object`: Export group to json 

### 🛡️ Group Rules

**Available Rules:**
- `GroupRule.NO_PVP` (0) - Players in the group cannot attack each other
- `GroupRule.NO_DAMAGE` (1) - Players in the group take no damage from any source
- `GroupRule.PVP_ONLY_GROUP` (3) - Players can only attack other players in the same group
- `GroupRule.NO_PVP_NO_DAMAGE` (4) - Combination of NO_PVP and NO_DAMAGE rules
- `GroupRule.NO_PVP_ONLY_GROUP` (5) - Players in the group cannot attack each other (PVP disabled within group only)

### 🎨 Boss Bar Customization

**Available Colors:**
- `BossBarColor.BLUE` (0) - Blue boss bar
- `BossBarColor.GREEN` (1) - Green boss bar  
- `BossBarColor.PINK` (2) - Pink boss bar
- `BossBarColor.PURPLE` (3) - Purple boss bar
- `BossBarColor.REBECCA_PURPLE` (4) - Rebecca purple boss bar
- `BossBarColor.RED` (5) - Red boss bar
- `BossBarColor.WHITE` (6) - White boss bar
- `BossBarColor.YELLOW` (7) - Yellow boss bar

**Available Styles:**
- `BossBarStyle.SOLID` (0) - Solid progress bar
- `BossBarStyle.SEGMENTED_6` (1) - 6 segments
- `BossBarStyle.SEGMENTED_10` (2) - 10 segments
- `BossBarStyle.SEGMENTED_12` (3) - 12 segments
- `BossBarStyle.SEGMENTED_20` (4) - 20 segments


## 📦 Installation

### For Add-on Developers (JavaScript/TypeScript)

1. Download the latest release from [GitHub Releases](https://github.com/Bedrock-Developpeur-Francophone/ScriptSDK/releases)
2. Copy the following files to your add-on project in a `lib` folder.

Your add-on structure should look like:
```
scripts/
├── lib/
│   ├── ScriptSDK.js
│   ├── ScriptSDK.d.ts
│   └── src/...
└── your-script.js
```

### For Server Administrators (Endstone Plugin)

1. Download the latest plugin wheel (`.whl`) from [GitHub Releases](https://github.com/Bedrock-Developpeur-Francophone/ScriptSDK/releases)
2. Place the `.whl` file in your Endstone server's `plugins` folder
3. Restart your server

## 🚀 Quick Start

### In your Bedrock Add-on

After copying the SDK files to your `lib` folder, import it in your main file:

```javascript
import 'lib/ScriptSDK'; // Initialisation of the library
```

### TypeScript Support

Full TypeScript support with type definitions included:

```typescript
import { Player } from '@minecraft/server';
import { BossBarColor, BossBarStyle } from 'lib/ScriptSDK';
import { GroupRule } from 'lib/src/enums';
import { Group } from 'lib/src/groups';

// TypeScript will provide autocomplete and type checking
const pvpGroup = new Group('PvPArena', GroupRule.PVP_ONLY_GROUP);
// Initialize the group before using it
await pvpGroup.init();

const setupPlayer = async (player: Player) => {
    
    await player.setBossBar('Health Bar', BossBarColor.RED, BossBarStyle.SOLID, 80);
    await pvpGroup.addPlayer(player);
};
```

## 📝 License

This project is licensed under the GPL-2.0 License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/Bedrock-Developpeur-Francophone/ScriptSDK)
- [Issue Tracker](https://github.com/Bedrock-Developpeur-Francophone/ScriptSDK/issues)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/Bedrock-Developpeur-Francophone/ScriptSDK/issues) on GitHub.