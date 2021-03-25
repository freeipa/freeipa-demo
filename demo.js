/*  Authors:
 *    Petr Vobornik <pvoborni@redhat.com>
 *
 * Copyright (C) 2014 Red Hat
 * see file 'COPYING' for use and warranty information
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
define([
        'freeipa/jquery',
        'freeipa/phases'
    ],
    function($, phases) {

var demo = {

    template: "<div id=\"demo_notice\">For more information about the public demo look at \
    <a href=\"http://www.freeipa.org/page/Demo\">demo wiki page</a>. \
    <a href=\"#\" class=\"dismiss\">Dismiss</a></div>",

    css: {
        position: 'absolute',
        top: '0px',
        left: '0px',
        'z-index': '100',
        'background-color': '#FFF',
        padding: '10px',
        border: "1px solid black"
    },

    render: function() {
        var $notice = $(this.template).appendTo($("body")).css(this.css);
        $(".dismiss", $notice).click(function() {
            $notice.remove();
        });
    }
};

phases.on('login', function() {
    demo.render();
    return true;
}, 20);

return demo;
});
