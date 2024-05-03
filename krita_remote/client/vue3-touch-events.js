/**
 * @project   vue3-touch-events
 * @author    Robin Rodricks, Xavier Julien, Jerry Bendy
 * @since     30/4/2021
 * @url       https://github.com/robinrodricks/vue3-touch-events
 */

function touchX(event) {
    if(event.type.indexOf('mouse') !== -1){
        return event.clientX;
    }
    return event.touches[0].clientX;
}

function touchY(event) {
    if(event.type.indexOf('mouse') !== -1){
        return event.clientY;
    }
    return event.touches[0].clientY;
}

function isOrthogonal(x, y) {
    const sqrt = Math.sqrt(x*x+y*y)
    const normX = Math.abs(x/sqrt)
    const normY = Math.abs(y/sqrt)
    const uV = 0.7071
    const dotProduct = normX*uV + normY*uV
    if (dotProduct > 0.95) {
        return false
    } else {
        return true
    }
}

var isPassiveSupported = (function() {
    var supportsPassive = false;
    try {
        var opts = Object.defineProperty({}, 'passive', {
            get: function() {
                supportsPassive = true;
            }
        });
        window.addEventListener('test', null, opts);
    } catch (e) {}
    return supportsPassive;
})();

var vueTouchEvents = {
    install: function (app, constructorOptions) {

        var globalOptions = Object.assign({}, {
            disableClick: false,
            tapTolerance: 10,  // px
            swipeTolerance: 40,  // px
            touchHoldTolerance: 400,  // ms
            longTapTimeInterval: 400,  // ms
            touchUpgradeWindow: 50, // ms
            touchClass: '',
                        dragFrequency: 100, // ms
                        rollOverFrequency: 100, // ms
        }, constructorOptions);

        function touchStartEvent(event) {
            var $this = this.$$touchObj,
                isTouchEvent = event.type.indexOf('touch') >= 0,
                isMouseEvent = event.type.indexOf('mouse') >= 0,
                $el = this;

            if (isTouchEvent && !$this.touchUpgraded) {
                $this.lastTouchStartTime = event.timeStamp;
            }

            if (isMouseEvent && $this.lastTouchStartTime && event.timeStamp - $this.lastTouchStartTime < 350) {
                return;
            }

            if ($this.initialTouchStarted && $this.pressTimer != null) {
                if (event.touches.length > 1 )
                {
                    cancelPressTimer($this);
                    $this.touchUpgraded = true;
                    $this.initialTouchID = event.touches[0].identifier
                    $this.touchUpgradedStartX = touchX(event);
                    $this.touchUpgradedStartY = touchY(event);
                    triggerEvent(event, this, 'multipress');
                }
                return;
            }

            addTouchClass(this);

            $this.initialTouchStarted = true; // always true while the element is being PRESSED by the first touch event
            $this.dropEnd = false; // true if future touchmove and touchend events should be ignored
            // the last valid X,Y values to ingest in future touch events
            $this.trueEndX = 0;
            $this.trueEndY = 0;

            $this.touchMoved = false; // true only when the element is PRESSED and DRAGGED a bit
            $this.touchUpgraded = false; // single touch -> multitouch

            $this.startX = touchX(event);
            $this.startY = touchY(event);

            $this.currentX = 0; // always updated with the last mouse X/Y while over the element
            $this.currentY = 0;

            $this.largestXDst = 0;
            $this.largestYDst = 0;
            $this.fartherX = touchX(event);
            $this.fartherY = touchY(event);

            $this.touchUpgradedStartX = null; // the start pos cannot be used for multitouch directional gestures
            $this.touchUpgradedStartY = null;

            $this.touchStartTime = event.timeStamp;
            // performance: only process swipe events if `swipe.*` event is registered on this element
            $this.hasSwipe =
                hasEvent(this, 'swipe.left') || hasEvent(this, 'swipe.right')
                || hasEvent(this, 'swipe.top') || hasEvent(this, 'swipe.bottom')
                || hasEvent(this, 'swipe.topleft') || hasEvent(this, 'swipe.topright')
                || hasEvent(this, 'swipe.bottomleft') || hasEvent(this, 'swipe.bottomright');

            $this.hasMultiSwipe =
                hasEvent(this, 'multiswipe.left') || hasEvent(this, 'multiswipe.right')
                || hasEvent(this, 'multiswipe.top') || hasEvent(this, 'multiswipe.bottom')
                || hasEvent(this, 'multiswipe.topleft') || hasEvent(this, 'multiswipe.topright')
                || hasEvent(this, 'multiswipe.bottomleft') || hasEvent(this, 'multiswipe.bottomright');

            $this.hasFlick =
                hasEvent(this, 'flick.left') || hasEvent(this, 'flick.right')
                || hasEvent(this, 'flick.top') || hasEvent(this, 'flick.bottom')
                || hasEvent(this, 'flick.topleft') || hasEvent(this, 'flick.topright')
                || hasEvent(this, 'flick.bottomleft') || hasEvent(this, 'flick.bottomright');

            $this.hasMultiFlick =
                hasEvent(this, 'multiflick.left') || hasEvent(this, 'multiflick.right')
                || hasEvent(this, 'multiflick.top') || hasEvent(this, 'multiflick.bottom')
                || hasEvent(this, 'multiflick.topleft') || hasEvent(this, 'multiflick.topright')
                || hasEvent(this, 'multiflick.bottomleft') || hasEvent(this, 'multiflick.bottomright');

            // performance: only start hold timer if the `hold` event is registered on this element
            if (hasEvent(this, 'hold')){

                // Trigger touchhold event after `touchHoldTolerance` MS
                $this.touchHoldTimer = setTimeout(function() {
                    $this.touchHoldTimer = null;
                    triggerEvent(event, $el, 'hold');
                }, $this.options.touchHoldTolerance);
            }

            $this.pressTimer = setTimeout(function() {
                $this.pressTimer = null;
                triggerEvent(event, $el, 'press');
            }, $this.options.touchUpgradeWindow);
        }

        function touchMoveEvent(event) {
            var $this = this.$$touchObj;

            if ($this.dropEnd) {
                return;
            }

                        var curX = touchX(event);
                        var curY = touchY(event);

                        var movedAgain = ($this.currentX != curX) || ($this.currentY != curY);

            $this.currentX = curX;
            $this.currentY = curY;

            if (!$this.touchUpgraded) {
                const absX = Math.abs($this.startX - $this.currentX);
                const absY = Math.abs($this.startY - $this.currentY);
                if (!$this.touchMoved) {
                    var tapTolerance = $this.options.tapTolerance;

                    $this.touchMoved = Math.abs($this.touchUpgraded ? $this.touchUpgradedStartX : $this.startX - $this.currentX) > tapTolerance ||
                                       Math.abs($this.touchUpgraded ? $this.touchUpgradedStartY : $this.startY - $this.currentY) > tapTolerance;

                    // trigger `drag.once` only once after mouse FIRST moved while dragging the element
                    // (`touchMoved` is the flag that indicates we no longer need to trigger this)
                    if($this.touchMoved){
                        cancelTouchHoldTimer($this);
                        triggerEvent(event, this, 'drag.once');
                    }

                // performance: only process swipe events if `swipe.*` event is registered on this element
                }

                if ($this.touchMoved && ($this.hasFlick || $this.hasSwipe)) {
                    if (absX > $this.largestXDst) {
                        $this.largestXDst = absX;
                        $this.farthestX = curX;
                    }
                    if (absY > $this.largestYDst) {
                        $this.largestYDst = absY;
                        $this.farthestY = curY;
                    }
                }

                // only trigger `rollover` event if cursor actually moved over this element
                if(hasEvent(this, 'rollover') && movedAgain){

                    // throttle the `rollover` event based on `rollOverFrequency`
                    var now = event.timeStamp;
                    var throttle = $this.options.rollOverFrequency;
                    if ($this.touchRollTime == null || now > ($this.touchRollTime + throttle)){
                        $this.touchRollTime = now;

                        triggerEvent(event, this, 'rollover');
                    }
                }

                // only trigger `drag` event if cursor actually moved and if we are still dragging this element
                if(hasEvent(this, 'drag') && $this.initialTouchStarted && $this.touchMoved && movedAgain){

                    // throttle the `drag` event based on `dragFrequency`
                    var now = event.timeStamp;
                    var throttle = $this.options.dragFrequency;
                    if ($this.touchDragTime == null || now > ($this.touchDragTime + throttle)){
                        $this.touchDragTime = now;

                        triggerEvent(event, this, 'drag');
                    }
                }
            } else {
                var absX = Math.abs($this.currentX - $this.touchUpgradedStartX);
                var absY = Math.abs($this.currentY - $this.touchUpgradedStartY);

                if (!$this.touchMoved) {
                    var tapTolerance = $this.options.tapTolerance;

                    $this.touchMoved = Math.abs($this.touchUpgradedStartX - $this.currentX) > tapTolerance ||
                                       Math.abs($this.touchUpgradedStartY - $this.currentY) > tapTolerance;

                    if($this.touchMoved){
                        cancelTouchHoldTimer($this);
                    }

                }

                if ($this.touchMoved && ($this.hasMultiSwipe || $this.hasMultiFlick)) {
                    if (absX > $this.largestXDst) {
                        $this.largestXDst = absX;
                        $this.farthestX = curX;
                    }
                    if (absY > $this.largestYDst) {
                        $this.largestYDst = absY;
                        $this.farthestY = curY;
                    }
                }
            }
        }

        function touchCancelEvent() {
            var $this = this.$$touchObj;

            cancelTouchHoldTimer($this);
            removeTouchClass(this);

            $this.initialTouchStarted = $this.touchMoved = false;
            $this.touchUpgraded = false;
            $this.startX = $this.startY = 0;
        }

        function touchEndEvent(event) {
            var $this = this.$$touchObj,
                isTouchEvent = event.type.indexOf('touch') >= 0,
                isMouseEvent = event.type.indexOf('mouse') >= 0;

            // ignore residual touches from multitouch events
            if (isTouchEvent) {
                if (event.touches.length >= 1 || (!$this.initialTouchStarted)) {
                    if (event.touches[0].identifier != $this.initialTouchID) {
                        // The touch events triggered by the first finger is used for gesture recognition,
                        // so once it has triggered its last touchend event, any future touchmove and touchend events
                        // triggered by the other fingers (or finger) should be ignored.
                        $this.dropEnd = true
                        $this.trueEndX = $this.currentX
                        $this.trueEndY = $this.currentY
                    }
                    return;
                }
                if ($this.dropEnd && event.touches.length == 0) {
                    // Since this is the last touchend event, we can finally make use of the last valid touch coordinates
                    $this.currentX = $this.trueEndX
                    $this.currentY = $this.trueEndY
                }
            }

            if (isTouchEvent) {
                $this.lastTouchEndTime = event.timeStamp;
            }

            var touchholdEnd = isTouchEvent && !$this.touchHoldTimer;
            cancelTouchHoldTimer($this);

            $this.initialTouchStarted = false;

            removeTouchClass(this);

            if (isMouseEvent && $this.lastTouchEndTime && event.timeStamp - $this.lastTouchEndTime < 350) {
                return;
            }

            // trigger `end` event when touch stopped
            if ($this.pressTimer) {
                clearTimeout($this.pressTimer);
                $this.pressTimer = null;
                triggerEvent(event, this, 'press');
            }

            triggerEvent(event, this, $this.touchUpgraded ? 'multirelease' : 'release');

            if (!$this.touchUpgraded) {
                if (!$this.touchMoved) {
                    // detect if this is a longTap event or not
                    if (hasEvent(this, 'longtap') && event.timeStamp - $this.touchStartTime > $this.options.longTapTimeInterval) {
                        if (event.cancelable) {
                            event.preventDefault();
                        }
                        triggerEvent(event, this, 'longtap');

                    } else if (hasEvent(this, 'hold') && touchholdEnd) {
                        if (event.cancelable) {
                            event.preventDefault();
                        }
                        return;
                    } else {
                        triggerEvent(event, this, 'tap');
                    }


                // performance: only process swipe events if `swipe.*` event is registered on this element
                } else if ($this.hasSwipe || $this.hasFlick) {

                    var curDstX = Math.abs($this.currentX - $this.startX);
                    var curDstY = Math.abs($this.currentY - $this.startY);

                    var flickX = curDstX < 0.5 * $this.largestXDst;
                    var flickY = curDstY < 0.5 * $this.largestYDst;

                    var direction,
                        flicking,
                        distanceY = Math.abs($this.startY - $this.farthestY),
                        distanceX = Math.abs($this.startX - $this.farthestX);

                    if (isOrthogonal(distanceX, distanceY)) {
                        if (distanceY > distanceX) {
                            direction = $this.startY > $this.farthestY ? 'top' : 'bottom';
                            flicking = flickY;
                        } else {
                            direction = $this.startX > $this.farthestX ? 'left' : 'right';
                            flicking = flickX;
                        }
                    } else {
                        var vertical_dir = $this.farthestY > $this.startY ? 'bottom' : 'top';
                        var horizontal_dir = $this.farthestX > $this.startX ? 'right' : 'left';
                        direction = `${vertical_dir}${horizontal_dir}`;
                        flicking = flickX && flickY;
                    }
                    if (hasEvent(this, 'flick.' + direction) && flicking) {
                        triggerEvent(event, this, 'flick.' + direction, direction);
                    }  else
                    if (hasEvent(this, 'swipe.' + direction) && !flicking) {
                        triggerEvent(event, this, 'swipe.' + direction, direction);
                    }
                }
            } else {
                if (hasEvent(this, 'multitap') && !$this.touchMoved) {
                    triggerEvent(event, this, 'multitap');
                } else if (($this.hasMultiSwipe || $this.hasMultiFlick)&& $this.touchMoved) {

                    var direction,
                        flicking,
                        distanceY = Math.abs($this.touchUpgradedStartY - $this.farthestY),
                        distanceX = Math.abs($this.touchUpgradedStartX - $this.farthestX);

                    var curDstX = Math.abs($this.currentX - $this.touchUpgradedStartX);
                    var curDstY = Math.abs($this.currentY - $this.touchUpgradedStartY);

                    var flickX = curDstX < 0.5 * $this.largestXDst;
                    var flickY = curDstY < 0.5 * $this.largestYDst;

                    if (isOrthogonal(distanceX, distanceY)) {
                        if (distanceY > distanceX) {
                            direction = $this.startY > $this.farthestY ? 'top' : 'bottom';
                            flicking = flickY;
                        } else {
                            direction = $this.startX > $this.farthestX ? 'left' : 'right';
                            flicking = flickX;
                        }
                    } else {
                        var vertical_dir = $this.farthestY > $this.startY ? 'bottom' : 'top';
                        var horizontal_dir = $this.farthestX > $this.startX ? 'right' : 'left';
                        direction = `${vertical_dir}${horizontal_dir}`;
                        flicking = flickX && flickY;
                    }
                    if (hasEvent(this, 'multiflick.' + direction) && flicking) {
                        triggerEvent(event, this, 'multiflick.' + direction, direction);
                    }  else
                    if (hasEvent(this, 'multiswipe.' + direction) && !flicking) {
                        triggerEvent(event, this, 'multiswipe.' + direction, direction);
                    }
                }
            }
        }

        function mouseEnterEvent() {
            addTouchClass(this);
        }

        function mouseLeaveEvent() {
            removeTouchClass(this);
        }

        function hasEvent($el, eventType) {
            var callbacks = $el.$$touchObj.callbacks[eventType];
                        return (callbacks != null && callbacks.length > 0);
                }

        function triggerEvent(e, $el, eventType, param) {
            var $this = $el.$$touchObj;

            // get the subscribers for this event
            var callbacks = $this.callbacks[eventType];

                        // exit if no subscribers to this particular event
            if (callbacks == null || callbacks.length === 0) {
                return null;
            }

                        // per callback
            for (var i = 0; i < callbacks.length; i++) {
                var binding = callbacks[i];

                if (binding.modifiers.stop) {
                    e.stopPropagation();
                }

                if (binding.modifiers.prevent) {
                    e.preventDefault();
                }

                // handle `self` modifier`
                if (binding.modifiers.self && e.target !== e.currentTarget) {
                    continue;
                }

                if (typeof binding.value === 'function') {
                    if (param) {
                        binding.value(param, e);
                    } else {
                        binding.value(e);
                    }
                }
            }
        }

        function addTouchClass($el) {
            var className = $el.$$touchObj.options.touchClass;
            className && $el.classList.add(className);
        }

        function removeTouchClass($el) {
            var className = $el.$$touchObj.options.touchClass;
            className && $el.classList.remove(className);
        }

        function cancelTouchHoldTimer($this) {
            if ($this && $this.touchHoldTimer) {
                clearTimeout($this.touchHoldTimer);
                $this.touchHoldTimer = null;
            }
        }

        function cancelPressTimer($this) {
            if ($this && $this.pressTimer) {
                clearTimeout($this.pressTimer);
                $this.pressTimer = null;
            }
        }

        function buildTouchObj($el, extraOptions) {
            var touchObj = $el.$$touchObj || {
                // an object contains all callbacks registered,
                // key is event name, value is an array
                callbacks: {},
                // prevent bind twice, set to true when event bound
                hasBindTouchEvents: false,
                // default options, would be override by v-touch-options
                options: globalOptions
            };
            if (extraOptions) {
                touchObj.options = Object.assign({}, touchObj.options, extraOptions);
            }
            $el.$$touchObj = touchObj;
            return $el.$$touchObj;
        }

        app.directive('touch', {
            beforeMount: function ($el, binding) {
                // build a touch configuration object
                var $this = buildTouchObj($el);
                // declare passive option for the event listener. Defaults to { passive: true } if supported
                var passiveOpt = isPassiveSupported ? { passive: true } : false;
                // register callback
                var eventType = binding.arg || 'tap';
                switch (eventType) {
                    case 'swipe':
                        var _m = binding.modifiers;
                        if (_m.left || _m.right || _m.top || _m.bottom || _m.topleft || _m.topright || _m.bottomleft || _m.bottomright) {
                            for (var i in binding.modifiers) {
                                if (['left', 'right', 'top', 'bottom', 'topleft', 'topright', 'bottomleft', 'bottomright'].indexOf(i) >= 0) {
                                    var _e = 'swipe.' + i;
                                    $this.callbacks[_e] = $this.callbacks[_e] || [];
                                    $this.callbacks[_e].push(binding);
                                }
                            }
                        } else {
                            $this.callbacks.swipe = $this.callbacks.swipe || [];
                            $this.callbacks.swipe.push(binding);
                        }
                        break;
                    case 'flick':
                        var _m = binding.modifiers;
                        if (_m.left || _m.right || _m.top || _m.bottom || _m.topleft || _m.topright || _m.bottomleft || _m.bottomright) {
                            for (var i in binding.modifiers) {
                                if (['left', 'right', 'top', 'bottom', 'topleft', 'topright', 'bottomleft', 'bottomright'].indexOf(i) >= 0) {
                                    var _e = 'flick.' + i;
                                    $this.callbacks[_e] = $this.callbacks[_e] || [];
                                    $this.callbacks[_e].push(binding);
                                }
                            }
                        } else {
                            $this.callbacks.flick = $this.callbacks.flick || [];
                            $this.callbacks.flick.push(binding);
                        }
                        break;
                    case 'multiswipe':
                        var _m = binding.modifiers;
                        if (_m.left || _m.right || _m.top || _m.bottom || _m.topleft || _m.topright || _m.bottomleft || _m.bottomrigh) {
                            for (var i in binding.modifiers) {
                                if (['left', 'right', 'top', 'bottom', 'topleft', 'topright', 'bottomleft', 'bottomright'].indexOf(i) >= 0) {
                                    var _e = 'multiswipe.' + i;
                                    $this.callbacks[_e] = $this.callbacks[_e] || [];
                                    $this.callbacks[_e].push(binding);
                                }
                            }
                        } else {
                            $this.callbacks.multiswipe = $this.callbacks.multiswipe || [];
                            $this.callbacks.multiswipe.push(binding);
                        }
                        break;
                    case 'multiflick':
                        var _m = binding.modifiers;
                        if (_m.left || _m.right || _m.top || _m.bottom || _m.topleft || _m.topright || _m.bottomleft || _m.bottomrigh) {
                            for (var i in binding.modifiers) {
                                if (['left', 'right', 'top', 'bottom', 'topleft', 'topright', 'bottomleft', 'bottomright'].indexOf(i) >= 0) {
                                    var _e = 'multiflick.' + i;
                                    $this.callbacks[_e] = $this.callbacks[_e] || [];
                                    $this.callbacks[_e].push(binding);
                                }
                            }
                        } else {
                            $this.callbacks.multiflick = $this.callbacks.multiflick || [];
                            $this.callbacks.multiflick.push(binding);
                        }
                        break;

                    case 'press':
                    case 'drag':
                    case 'multitap':
                    case 'multipress':
                        if (binding.modifiers.disablePassive) {
                            // change the passive option for the `drag` event if disablePassive modifier exists
                            passiveOpt = false;
                        }
                    default:
                        $this.callbacks[eventType] = $this.callbacks[eventType] || [];
                        $this.callbacks[eventType].push(binding);
                }

                // prevent bind twice
                if ($this.hasBindTouchEvents) {
                    return;
                }

                $el.addEventListener('touchstart', touchStartEvent, passiveOpt);
                $el.addEventListener('touchmove', touchMoveEvent, passiveOpt);
                $el.addEventListener('touchcancel', touchCancelEvent);
                $el.addEventListener('touchend', touchEndEvent);

                if (!$this.options.disableClick) {
                    $el.addEventListener('mousedown', touchStartEvent);
                    $el.addEventListener('mousemove', touchMoveEvent);
                    $el.addEventListener('mouseup', touchEndEvent);
                    $el.addEventListener('mouseenter', mouseEnterEvent);
                    $el.addEventListener('mouseleave', mouseLeaveEvent);
                }

                // set bind mark to true
                $this.hasBindTouchEvents = true;
            },

            unmounted: function ($el) {
                cancelTouchHoldTimer($el.$$touchObj)

                $el.removeEventListener('touchstart', touchStartEvent);
                $el.removeEventListener('touchmove', touchMoveEvent);
                $el.removeEventListener('touchcancel', touchCancelEvent);
                $el.removeEventListener('touchend', touchEndEvent);

                if ($el.$$touchObj && !$el.$$touchObj.options.disableClick) {
                    $el.removeEventListener('mousedown', touchStartEvent);
                    $el.removeEventListener('mousemove', touchMoveEvent);
                    $el.removeEventListener('mouseup', touchEndEvent);
                    $el.removeEventListener('mouseenter', mouseEnterEvent);
                    $el.removeEventListener('mouseleave', mouseLeaveEvent);
                }

                // remove vars
                delete $el.$$touchObj;
            }
        });

        app.directive('touch-class', {
            beforeMount: function ($el, binding) {
                buildTouchObj($el, {
                    touchClass: binding.value
                });
            }
        });

        app.directive('touch-options', {
            beforeMount: function($el, binding) {
                buildTouchObj($el, binding.value);
            }
        });
    }
};

/*
 * Exports
 */
export default vueTouchEvents
