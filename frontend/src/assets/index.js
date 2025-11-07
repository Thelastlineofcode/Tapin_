/* eslint-disable unicorn/prefer-export-from */
// Centralized asset exports for the frontend
// ES module format for Vite compatibility

// Prefer vector brand assets when available
import logoSvg from '../../../Design-Assets/brand/logo.svg';
import logoMono from '../../../Design-Assets/brand/logo-monochrome.svg';
import logoReversed from '../../../Design-Assets/brand/logo-reversed.svg';
import logoTransparent from '../../../Design-Assets/brand/logo-transparent.svg';
import pngLogo from '../../../Design-Assets/Tapin-Logo.png';
import wireframe from '../../../Design-Assets/Wireframe.png';

const logo = logoTransparent || logoSvg || pngLogo;

export { logo, logoSvg, logoMono, logoReversed, logoTransparent, pngLogo as logoPng, wireframe };
