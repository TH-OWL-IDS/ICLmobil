#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

module.exports = function(context) {
    // Only run for Android platform
    if (context.opts.platforms.indexOf('android') < 0) {
        return;
    }

    const splashscreenPath = path.join(
        context.opts.projectRoot,
        'platforms',
        'android',
        'app',
        'src',
        'main',
        'res',
        'drawable',
        'ic_cdv_splashscreen.xml'
    );

    const themesPath = path.join(
        context.opts.projectRoot,
        'platforms',
        'android',
        'app',
        'src',
        'main',
        'res',
        'values',
        'themes.xml'
    );

    // Check if the file exists and remove it
    if (fs.existsSync(splashscreenPath)) {
        try {
            fs.unlinkSync(splashscreenPath);
            console.log('✓ Removed ic_cdv_splashscreen.xml');
        } catch (error) {
            console.error('Error removing ic_cdv_splashscreen.xml:', error.message);
        }
    } else {
        console.log('ic_cdv_splashscreen.xml not found, skipping removal');
    }

    // Remove the reference from themes.xml
    if (fs.existsSync(themesPath)) {
        try {
            let themesContent = fs.readFileSync(themesPath, 'utf8');
            
            // Remove the line that references ic_cdv_splashscreen
            themesContent = themesContent.replace(/^\s*<item name="windowSplashScreenAnimatedIcon">@drawable\/ic_cdv_splashscreen<\/item>\s*$/gm, '');
            
            fs.writeFileSync(themesPath, themesContent);
            console.log('✓ Removed ic_cdv_splashscreen reference from themes.xml');
        } catch (error) {
            console.error('Error updating themes.xml:', error.message);
        }
    } else {
        console.log('themes.xml not found, skipping reference removal');
    }

    // Update the splash screen background color to match Lottie
    const colorsPath = path.join(
        context.opts.projectRoot,
        'platforms',
        'android',
        'app',
        'src',
        'main',
        'res',
        'values',
        'colors.xml'
    );

    if (fs.existsSync(colorsPath)) {
        try {
            let colorsContent = fs.readFileSync(colorsPath, 'utf8');
            
            // Update the background color to match your Lottie background
            colorsContent = colorsContent.replace(
                /<color name="cdv_splashscreen_background">#[A-Fa-f0-9]+<\/color>/,
                '<color name="cdv_splashscreen_background">#103d1a</color>'
            );
            
            fs.writeFileSync(colorsPath, colorsContent);
            console.log('✓ Updated splash screen background color to match Lottie');
        } catch (error) {
            console.error('Error updating colors.xml:', error.message);
        }
    } else {
        console.log('colors.xml not found, skipping color update');
    }
};
