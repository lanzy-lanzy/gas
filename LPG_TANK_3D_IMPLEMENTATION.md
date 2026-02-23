# LPG Tank 3D Visualization - Three.js Implementation

## Overview
Added an interactive 3D LPG tank visualization to the landing page background using Three.js. The tank is rendered on a full-screen canvas in the hero section with realistic physics and user interactions.

## Features Implemented

### 3D Components
- **Main Tank Body**: Cylindrical container with metallic material
- **Tank Caps**: Hemispherical top and bottom caps
- **Valve**: Top-mounted valve mechanism
- **Gauge**: Pressure gauge indicator on the side
- **Liquid Level**: Animated transparent liquid showing fill level (65% full)
- **Support Legs**: Four sturdy support legs for stability

### Visual Features
- **Realistic Materials**: MeshStandardMaterial with metalness and roughness properties
- **Dynamic Lighting**: Multiple light sources (ambient, point lights, and directional light)
- **Color Scheme**: Orange and gray colors matching brand identity (#ff6b35, #e55a2b)
- **Emissive Materials**: Glowing effect on tank and liquid to enhance visibility
- **Floating Animation**: Smooth vertical bobbing motion
- **Mouse Interaction**: Tank rotates based on mouse movement across the screen

### Performance Optimizations
- Antialiasing enabled for smooth edges
- Device pixel ratio handling for crisp rendering on high-DPI displays
- Transparent canvas background to blend with gradient
- Responsive resize handling for all screen sizes

## File Modified
**`c:/Users/ROCHELLE/dev/prycegas/templates/test_base.html`**

### Changes Made:

1. **Added Three.js CDN Script** (Line ~48)
   ```html
   <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
   ```

2. **Added CSS Styles** (Lines ~122-134)
   - `#lpg-tank-canvas`: Full-screen absolute positioned canvas
   - `.hero-content-wrapper`: Relative positioning for z-index layering

3. **Added Canvas Element** (Line ~153)
   ```html
   <canvas id="lpg-tank-canvas"></canvas>
   ```

4. **Added JavaScript Initialization** (Lines ~722-920)
   - `initLPGTankScene()`: Main initialization function
   - Scene, camera, and renderer setup
   - Geometry creation for all tank components
   - Material definitions with metallic properties
   - Lighting setup with multiple light sources
   - Animation loop with mouse tracking
   - Window resize handling

## How It Works

### Initialization
- Function runs on `DOMContentLoaded` event
- Creates Three.js scene with proper camera aspect ratio
- Builds all 3D components and adds to scene
- Starts continuous animation loop

### Animation
- **Floating Motion**: `Math.sin(Date.now() * 0.001) * 0.3` creates smooth vertical animation
- **Mouse Tracking**: Tracks mouse position and rotates tank accordingly
- **Slow Rotation**: Tank slowly spins on Z-axis for visual interest
- **Smooth Interpolation**: Uses `0.05` factor for smooth rotation transitions

### Interactive Elements
- **Mouse Position Tracking**: Captures mouse coordinates
- **Responsive Rotation**: Tank rotates to face mouse cursor
- **Window Resize**: Canvas automatically scales to window dimensions

## Browser Compatibility
- Requires WebGL support
- Works on all modern browsers (Chrome, Firefox, Safari, Edge)
- Falls back gracefully if WebGL not available

## Performance Considerations
- Full-screen 3D rendering at 60 FPS
- Optimized for desktop and tablet viewing
- Mobile performance may vary based on device capabilities
- Canvas transparency allows gradient background to show through

## Customization Options

### Adjust Tank Fill Level
Edit line 822 in the script:
```javascript
liquid.scale.y = 0.65; // Change to 0.5 for 50%, 0.8 for 80%, etc.
```

### Change Tank Color
Edit line 813:
```javascript
color: 0xff6b35, // Change hex value for different color
```

### Adjust Rotation Speed
Edit line 912:
```javascript
tank.rotation.z += 0.0005; // Increase for faster rotation
```

### Modify Floating Speed
Edit line 905:
```javascript
const floatOffset = Math.sin(Date.now() * 0.001) * 0.3; // 0.001 is speed, 0.3 is height
```

## Future Enhancements
- Add pressure gauge needle animation
- Implement tank capacity percentage display
- Add liquid sloshing physics
- Create multiple tank types (horizontal, vertical)
- Add pressure relief valve animation
- Implement touch controls for mobile
- Add temperature/pressure indicators
- Create tank inventory status visualization

## Testing
- Test on various screen sizes
- Verify mouse interactions work smoothly
- Check performance on different devices
- Validate responsive behavior on mobile
- Test WebGL compatibility across browsers
