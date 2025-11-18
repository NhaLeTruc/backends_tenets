# RogueLegacy1

This is the official source code release of Rogue Legacy 1, the roguelike action-platformer by Cellar Door Games (v1.4.1). It's a substantial C# game project with some impressive characteristics:

Project Overview
Technology Stack:

Language: C# (.NET Framework 4.0 + .NET 8.0 Core)
Framework: FNA (XNA reimplementation) with SDL3 backend
Platform: Cross-platform (Windows, Linux, macOS)
Build: Supports NativeAOT compilation for optimized performance
Architecture
5 Main Projects:

RogueCastle - Main game (213 C# files)
DS2DEngine - Custom 2D game engine
SpriteSystem - Sprite/animation management
InputSystem - Input handling
Tweener - Animation tweening library
Key Features & Systems
Core Systems:

Procedural Generation - Massive LevelBuilder2.cs (129KB) handles dungeon generation
AI System - Composable action-based behaviors for enemies
Save System - Complex save/load manager (125KB)
Skill Tree - Player progression system
Enemy System - 18+ enemy types with configurable stats
Equipment System - Loot and player gear
Localization - 8 languages (English, German, Spanish, French, Polish, Portuguese, Russian, Chinese)
Graphics:

30+ HLSL shader effects
Advanced lighting (crepuscular rays, gaussian blur, particles)
Custom sprite batching
Notable Architecture Patterns:

Entity-component system with base classes (GameObj, SpriteObj, PhysicsObj)
Object pooling for performance
Data-driven design using "EV" (Environment Variables) files for all game constants
Screen management system
Event trigger system
Code Quality Indicators
✅ Well-organized - Clear separation into Screens, Managers, Game Objects, Types
✅ Professional - Proper use of interfaces, enums, structs
✅ Configurable - All constants externalized to EV files
✅ Modern CI/CD - GitHub Actions with standard + NativeAOT builds
✅ Debug-friendly - Extensive debug flags and VSCode configuration

Interesting Finds
Largest file: EnemyEV.cs (163KB) - all enemy stats and configurations
Most complex: LevelBuilder2.cs - procedural dungeon generation algorithm
Steam integration - Optional Steamworks support
Non-commercial license - Code is released for educational/modding purposes
No assets included - You need to own the game to get art/audio
This is a production-quality game codebase demonstrating solid game development practices with extensive systems, proper architecture, and good maintainability.