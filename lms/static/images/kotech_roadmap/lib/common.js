const FEED_COLOR = '#d3f9d8';
const NORMAL_COLOR = '#d0ebff';
const EXIST_COLOR = '#ffe3e3';
const NULL_COLOR = '#f1f3f5';
const MATCH_COLOR = '#dbe4ff';

var OP_LOW = 0.1;
var OP_MID = 0.5;
var OP_HIGH = 1;

var VIS_SHAPE = 'box';

var network = null;

function vis_draw(nodes, edges) {
    if (network !== null) {
        network.destroy();
        network = null;
    }
    // create the network
    var container = document.getElementById("mynetwork");
    var data = {
        nodes: nodes,
        edges: edges
    };
    var options = {
        layout: {
            randomSeed: undefined,
            improvedLayout: true,
            hierarchical: {
                enabled: true,
                levelSeparation: 100,        // 계층 간 높이
                nodeSpacing: 100,
                treeSpacing: 200,
                blockShifting: true,
                edgeMinimization: true,
                parentCentralization: true,
                direction: 'UD',            // UD, DU, LR, RL
                sortMethod: 'directed',     // hubsize, directed
            }
        },
        nodes: {
            borderWidth: 1,
            borderWidthSelected: 2,
            brokenImage: undefined,
            chosen: true,
            color: {
                border: '#dddddd',                  // 노드 선 색상
                background: '#dddddd',              // 노드 박스 색상
                highlight: {
                    border: '#dddddd',                // select 노드 선 색
                    background: '#dddddd'             // select 노드 박스 색상
                },
                hover: {
                    border: '#dddddd',                // hover 노드 선 색
                    background: '#dddddd'             // hover 노드 박스 색상
                }
            },
            fixed: {
                x: false,
                y: false
            },
            size: 25,                             // 노드 크기
        },
        edges: {
            arrows: {
                to: {
                    enabled: true,
                    scaleFactor: 0.5,                 // 화살표 크기
                    type: "circle"
                },
                middle: {
                    enabled: false,
                    scaleFactor: 1,
                    type: "arrow"
                },
                from: {
                    enabled: false,
                    scaleFactor: 1,
                    type: "arrow"
                }
            },
            chosen: true,
            color: {
                color: '#848484',                    // 기본 엣지 색상
                highlight: '#4185c4',                // select 시 엣지 색상
                hover: '#4185c4',                   // hover 시 엣지 색상
                inherit: 'from',
                opacity: 1.0
            },
            dashes: false,                        // 엣지 대시 스타일
            hoverWidth: 2,                        // hover 시 엣지 굵기
            selectionWidth: 2,                    // select 시 엣지 굵기
        },
        interaction: {
            dragNodes: true,                      // 노드 드래그 여부
            dragView: true,                       // 뷰 드래그 여부
            hover: true,                          // 호버 이벤트 활성화 여부
            hoverConnectedEdges: true,            // 엣지 하이라이팅 여부 (hover)
            keyboard: {
                enabled: false,                     // 키보드 컨트롤 여부
                speed: {x: 10, y: 10, zoom: 0.02},
                bindToWindow: true
            },
            multiselect: false,
            navigationButtons: false,
            selectable: true,
            selectConnectedEdges: true,           // 엣지 하이라이팅 여부 (select)
            tooltipDelay: 300,                    // 툴팁 보여주는 딜레이
            zoomView: true                        // 확대 축소 기능 활성화 여부
        },
        physics: {
            enabled: true,
            hierarchicalRepulsion: {
                centralGravity: 0.0,
                springLength: 100,
                springConstant: 0.01,
                nodeDistance: 200,                // 노드 간 가로 간격
                damping: 0.09
            },
            maxVelocity: 50,
            minVelocity: 0.1,
            solver: 'hierarchicalRepulsion',
            stabilization: {
                enabled: true,
                iterations: 1000,
                updateInterval: 100,
                onlyDynamicEdges: false,
                fit: true
            },
            timestep: 0.5,
            adaptiveTimestep: true,
        }
    };
    network = new vis.Network(container, data, options);

    var networkCanvas = document.getElementById('mynetwork').getElementsByTagName('canvas')[0];

    function changeCursor(newCursorStyle) {
        networkCanvas.style.cursor = newCursorStyle;
    }

    // 마우스 포인터
    network.on("hoverNode", function (properties) {
        if (properties.node >= 0 && nodes[properties.node]['link'] && nodes[properties.node]['link'] !== '') {
            changeCursor('pointer');
        }
    });

    network.on("blurNode", function () {
        changeCursor('default');
    });

    // 노드 클릭 시 새탭 열기 이벤트 바인딩 (커스텀)
    network.on('click', function (properties) {
        // alert(properties.clientX + ":" + properties.clientY);

        var node_id = properties.nodes[0];
        // console.log(node_id);

        if (node_id != null) {
            var sNodeLabel = this.body.nodes[node_id].options.link;
        } else {
            $('#roadmap_pop').hide();
        }

        // 링크정보가 array 면 레이어 생성되었으나 전체적으로 레이어를 생성하여 동작하도록 통일

        if (node_id != null) {
            var canvasPosition = $('.vis-network').position();
            var layer_div = $('#roadmap_pop');
            var clickX = properties.pointer.DOM.x + canvasPosition.top - 40;
            var clickY = properties.pointer.DOM.y + canvasPosition.left + 10;

            if ($('.other-cont p.ctxt').length) {
                $('.other-cont').empty();
            }

            let title = this.body.nodes[node_id].options.label;
            if (title.indexOf(')') > 0)
                title = title.substring(0, title.indexOf(')') + 1);

            $('div.roadmap_header').html(title);

            if ($.type(sNodeLabel) === 'array') {
                for (let i = 0; i < sNodeLabel.length; i++) {

                    let url = sNodeLabel[i][1];

                    if (url) {
                        if (url.startsWith('http')) {
                            $('div.other-cont').append('<a target="_blank" href="' + sNodeLabel[i][1] + '"><p class="ctxt mb20">' + sNodeLabel[i][0] + '</p></a>');
                        } else {
                            $('div.other-cont').append('<a href="javascript: roadmapLink(\'' + encodeURIComponent(sNodeLabel[i][1]) + '\')"><p class="ctxt mb20">' + sNodeLabel[i][0] + '</p></a>');
                        }
                    } else {
                        $('div.other-cont').append('<a href="#"><p class="ctxt mb20">' + sNodeLabel[i][0] + '</p></a>');
                    }
                }

                layer_div.css('top', clickY).css('left', clickX).show();

            } else {

                let link = nodes[node_id]['link'];

                if (link) {

                    if (link.startsWith('http')) {
                        console.log('link check ------------------------------- s');
                        console.log(link);
                        console.log('link check ------------------------------- e');
                        // $('div.other-cont').append('<a href="'+ link +'" target="_blank"><p class="ctxt mb20">' + c.display_name + ' (' + c.org_name +')</p></a>');
                        // layer_div.css('top', clickY).css('left', clickX).show();
                    } else {
                        $.ajax({
                            method: "get",
                            url: "",
                            async: false,
                            data: {
                                data: link
                            },
                            dataType: "json",
                            complete: function (d) {
                                let c = d.responseJSON;

                                $('div.other-cont').append('<a href="' + c.url + '" target="_blank"><p class="ctxt mb20">' + c.display_name + ' (' + c.org_name + ')</p></a>');
                                layer_div.css('top', clickY).css('left', clickX).show();

                            }
                        });
                    }


                }
            }


        } else {
            roadmapLink();
        }

        /*
        if ($.type(sNodeLabel) === 'array') {
            var canvasPosition = $('.vis-network').position();
            var layer_div = $('#roadmap_pop');
            var clickX = properties.pointer.DOM.x + canvasPosition.top - 40;
            var clickY = properties.pointer.DOM.y + canvasPosition.left + 10;

            if ($('.other-cont p.ctxt').length) {
                $('.other-cont').empty();
            }

            for (let i = 0; i < sNodeLabel.length; i++) {
                // sNodeLabel[i][0] : 강좌명
                // sNodeLabel[i][1] : 링크
                $('div.other-cont').append('<a href="javascript: roadmapLink(\'' + encodeURIComponent(sNodeLabel[i][1]) + '\')"><p class="ctxt mb20">' + sNodeLabel[i][0] + '</p></a>');
            }

            layer_div.css('top', clickY).css('left', clickX).show();

        } else if (node_id != null) {
            roadmapLink(nodes[node_id]['link']);
        } else {
            roadmapLink();
        }
        */


    });
}

function roadmapClose() {
    $('.roadmap_header').empty();
    $('.other-cont').empty();
    $('#roadmap_pop').hide();
}

function roadmapLink(link) {
    if (link && link !== '') {

        $.get('', {data: link}).done(function (d) {
            if (d.url) {
                window.open(d.url, "_blank");
            } else {
                swal('', d.error, 'info');
            }
        });
    }
}
