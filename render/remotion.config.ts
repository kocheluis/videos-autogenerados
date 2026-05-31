import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// Si hay problemas de WebGL en headless, descomentar:
// Config.setChromiumOpenGlRenderer("angle");
