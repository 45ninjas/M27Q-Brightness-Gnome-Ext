import Gio from 'gi://Gio';
import GObject from 'gi://GObject';

import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as QuickSettings from 'resource:///org/gnome/shell/ui/quickSettings.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

const MonitorBrightnessItem = GObject.registerClass(
class MonitorBrightnessItem extends QuickSettings.QuickSlider {
    _init(val) {
        super._init({
            iconName: 'display-brightness-symbolic',
        });

        this._sliderChangedId = this.slider.connect('notify::value',
            this._onSliderChanged.bind(this));
        this.slider.accessible_name = _('Brightness');
        this.slider.value = val / 100;
        
    }
    
    _onSliderChanged() {
        const percent = Math.floor(this.slider.value * 100);
        //console.log(`slider changed to ${percent}`);
        brightness(percent);
    }
});
export default class Mq27Brightness extends Extension {
    enable() {
    	path = this.path;
    	const val = brightness("false");
    	const myIndicator = new QuickSettings.SystemIndicator();
    	
    	if(Number.isInteger(val)) {
        	myIndicator.quickSettingsItems.push(new MonitorBrightnessItem(val));
        	Main.panel.statusArea.quickSettings.addExternalIndicator(myIndicator, 2); 
    	} else {
    	    logError('The monitor was not found. Have you got the udev rule installed?');
    	}    
    }

    disable() {
        this.myIndicator?.destroy();
        this.myIndicator = null;
    }
}
let path = "";
function brightness(value) {  
    const proc = Gio.Subprocess.new(['python', path + '/brightness.py',
    value.toString()], Gio.SubprocessFlags.STDOUT_PIPE);
    
    const [success, stdout] = proc.communicate_utf8(null, null);
    console.log(proc.get_exit_status());
    
    if (proc.get_successful())
        return Number.parseInt(stdout);
    else if (stdout.startsWith("Device VID_"))
        return false;
    else
        throw(`Failed to run python script: ${stdout}`);
}
