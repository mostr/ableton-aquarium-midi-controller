# emacs-mode: -*- python-*-
# -*- coding: utf-8 -*-

import Live
from _Framework.SessionComponent import SessionComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.SubjectSlot import subject_slot
import logging
logger = logging.getLogger(__name__)
import time


class SpecialClipSlotComponent(ClipSlotComponent):

    def __init__(self, *a, **k):
        super(SpecialClipSlotComponent, self).__init__(*a, **k)
        now = int(round(time.time() * 1000))
        self._last_press = now
        return

    @subject_slot('value')
    def _launch_button_value(self, value):
        logger.info("launch" + str(value))
        now = int(round(time.time() * 1000))
        if value != 0:
            self._last_press = now
        else:
            if now - self._last_press > 500: # 0.5s
                self._clip_slot.delete_clip()
            else:
                logger.info("do launch")
                self._do_launch_clip(value)
        return

    def _do_launch_clip(self, value):
        button = self._launch_button_value.subject
        object_to_launch = self._clip_slot
        launch_pressed = value or not button.is_momentary()
        if self.has_clip():
            object_to_launch = self._clip_slot.clip
        else:
            self._has_fired_slot = True
        if button.is_momentary():
            object_to_launch.set_fire_button_state(value == 0)
        elif launch_pressed:
            object_to_launch.fire()
        if launch_pressed and self.has_clip() and self.song().select_on_launch:
            self.song().view.highlighted_clip_slot = self._clip_slot
            
class SpecialSceneComponent(SceneComponent):
    
    clip_slot_component_type = SpecialClipSlotComponent

    def __init__(self, *a, **k):
        self._duplicate_button = None
        SceneComponent.__init__(self, *a, **k)
        now = int(round(time.time() * 1000))
        self._last_press = now


    def set_duplicate_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._duplicate_button != button):
            if (self._duplicate_button != None):
                self._duplicate_button.remove_value_listener(self._duplicate_value)
            self._duplicate_button = button
            if (self._duplicate_button != None):
                self._duplicate_button.add_value_listener(self._duplicate_value)

            self.update()

    def _duplicate_value(self, value):
        now = int(round(time.time() * 1000))
        if value != 0:
            self._last_press = now
        else:
            logger.info("time: " + str(now - self._last_press))
            if now - self._last_press > 500: # 0.5s
                prev_scene_index = max(list(self.song().scenes).index(self._scene) - 1, 0)
                self._do_delete_scene(self._scene)
                self.song().view.selected_scene = self.song().scenes[prev_scene_index]
            else:
                logger.info("regular - duplicate")
                self._do_duplicate_scene()
        return

    # def selected_scene_idx(self):
    #     logger.info(str(self.song().scenes))
	# 	a = list(self.song().scenes).index(self._scene)
    #     logger.info(str(a))
    #     a

    def _do_duplicate_scene(self):
        try:
            song = self.song()
            song.duplicate_scene(list(song.scenes).index(self._scene))
        except Live.Base.LimitationError:
            pass
        except RuntimeError:
            pass
        except IndexError:
            pass



class SpecialSessionComponent(SessionComponent):
    " Special SessionComponent for APC combination mode and button to fire selected clip slot "
    __module__ = __name__

    scene_component_type = SpecialSceneComponent

    def __init__(self, num_tracks, num_scenes):
        SessionComponent.__init__(self, num_tracks, num_scenes)
        self._slot_launch_button = None


    def disconnect(self):
        SessionComponent.disconnect(self)
        if (self._slot_launch_button != None):
            self._slot_launch_button.remove_value_listener(self._slot_launch_value)
            self._slot_launch_button = None


    def link_with_track_offset(self, track_offset, scene_offset):
        assert (track_offset >= 0)
        assert (scene_offset >= 0)
        if self._is_linked():
            self._unlink()
        self.set_offsets(track_offset, scene_offset)
        self._link()


    def unlink(self):
        if self._is_linked():
            self._unlink()


    def set_slot_launch_button(self, button):
        assert ((button == None) or isinstance(button, ButtonElement))
        if (self._slot_launch_button != button):
            if (self._slot_launch_button != None):
                self._slot_launch_button.remove_value_listener(self._slot_launch_value)
            self._slot_launch_button = button
            if (self._slot_launch_button != None):
                self._slot_launch_button.add_value_listener(self._slot_launch_value)

            self.update()


    def _slot_launch_value(self, value):
        assert (value in range(128))
        assert (self._slot_launch_button != None)
        if self.is_enabled():
            if ((value != 0) or (not self._slot_launch_button.is_momentary())):
                if (self.song().view.highlighted_clip_slot != None):
                    self.song().view.highlighted_clip_slot.fire()



# local variables:
# tab-width: 4
