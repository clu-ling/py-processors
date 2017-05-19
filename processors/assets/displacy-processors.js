//- ----------------------------------
//- 💥 DISPLACY
//- ----------------------------------



'use strict';

class displaCyProcessors {
    constructor (options) {

        this.container = document.querySelector(options.container || '#displacy');

        this.$ = document.querySelector.bind(document);

        this.onStart = options.onStart || false;
        this.onSuccess = options.onSuccess || false;
        this.onError = options.onError || false;

        this.distance = options.distance || 200;
        this.offsetX = options.offsetX || 50;
        this.arrowSpacing = options.arrowSpacing || 20;
        this.arrowWidth = options.arrowWidth || 10;
        this.arrowStroke = options.arrowStroke || 2;
        this.wordSpacing = options.wordSpacing || 75;
        this.font = options.font || 'inherit';
        this.color = options.color || '#000000';
        this.bg = options.bg || '#ffffff';
    }

    exportSVG() {
      // http://stackoverflow.com/a/38481556
      var parseStyles = function(svg) {
        var styleSheets = [];
        var i;
        // get the stylesheets of the document (ownerDocument in case svg is in <iframe> or <object>)
        var docStyles = svg.ownerDocument.styleSheets;

        // transform the live StyleSheetList to an array to avoid endless loop
        for (i = 0; i < docStyles.length; i++) {
          styleSheets.push(docStyles[i]);
        }

        if (!styleSheets.length) {
          return;
        }

        var defs = svg.querySelector('defs') || document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        if (!defs.parentNode) { svg.insertBefore(defs, svg.firstElementChild); }
        svg.matches = svg.matches || svg.webkitMatchesSelector || svg.mozMatchesSelector || svg.msMatchesSelector || svg.oMatchesSelector;

        // iterate through all document's stylesheets
        for (i = 0; i < styleSheets.length; i++) {
          var currentStyle = styleSheets[i]

          var rules;
          try {
            rules = currentStyle.cssRules;
          } catch (e) {
            continue;
          }
          // create a new style element
          var style = document.createElement('style');
          // some stylesheets can't be accessed and will throw a security error
          var l = rules && rules.length;
          // iterate through each cssRules of this stylesheet
          for (var j = 0; j < l; j++) {
            // get the selector of this cssRules
            var selector = rules[j].selectorText;
            // probably an external stylesheet we can't access
            if (!selector) {
              continue;
            }

            // is it our svg node or one of its children ?
            if ((svg.matches && svg.matches(selector)) || svg.querySelector(selector)) {

              var cssText = rules[j].cssText;
              // append it to our <style> node
              style.innerHTML += cssText + '\n';
            }
          }
          // if we got some rules
          // append the style node to the clone's defs
          if (style.innerHTML) { defs.appendChild(style); }
        }
      }

      var svg = this.$("#" + this.getSVGname())
      // first create a clone of our svg node so we don't mess the original one
      var clone = svg.cloneNode(true);
      // parse the styles
      parseStyles(clone);
      // create a doctype
      var svgDocType = document.implementation.createDocumentType('svg', "-//W3C//DTD SVG 1.1//EN", "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd");
      // a fresh svg document
      var svgDoc = document.implementation.createDocument('http://www.w3.org/2000/svg', 'svg', svgDocType);
      // replace the documentElement with our clone
      svgDoc.replaceChild(clone, svgDoc.documentElement);
      // get the data
      var svgData = (new XMLSerializer()).serializeToString(svgDoc);

      var a = document.createElement('a');
      a.href = 'data:image/svg+xml; charset=utf8, ' + encodeURIComponent(svgData.replace(/></g, '>\n\r<'));
      a.download = 'graph.svg';
      a.innerHTML = 'save to file';
      this.container.appendChild(a);
    }

    handleParsedSentence(sentence, graphName = "stanford-collapsed") {
        return ({
          words: sentence.words.map((w, i) => ({
            text: sentence.words[i],
            tag: sentence.tags[i],
            lemma: sentence.lemmas[i],
            entity: sentence.entities[i]
            // data: [
            //   ["lemmas", sentence.lemmas[i]],
            //   ["entities", sentence.entities[i]]
            // ]
          })),
          // conversions are to ensure edge label is properly rotated
          arcs: sentence.graphs[graphName].edges.map(({ relation: rel, source: src, destination: dest}, i) => ({
              label: rel,
              start: Math.min(dest, src),
              end: Math.max(dest, src),
              dir: ((src > dest) ? 'left' : 'right')
          }))
        })
    }
    getSVGname() {return this.container.id + '-svg'; }
    render(sentence, graphName = "stanford-collapsed", settings = {}, text) {
        var parse = this.handleParsedSentence(sentence, graphName = "stanford-collapsed");
        this.levels = [...new Set(parse.arcs.map(({ end, start }) => end - start).sort((a, b) => a - b))];
        // starting node for most distant dependency
        // (note that disregard for sign means )
        this.highestLevel = this.levels.indexOf(this.levels.slice(-1)[0]) + 1;
        this.offsetY = this.distance / 2 * this.highestLevel;

        const width = this.offsetX + parse.words.length * this.distance;
        const height = this.offsetY + 3 * this.wordSpacing;

        this.container.innerHTML = '';
        this.container.appendChild(this._el('svg', {
            id: this.getSVGname(),
            classnames: [ 'displacy' ],
            attributes: [
                [ 'width', width ],
                [ 'height', height ],
                [ 'viewBox', `0 0 ${width} ${height}`],
                [ 'preserveAspectRatio', 'xMinYMax meet' ],
                [ 'data-format', this.format ]
            ],
            style: [
                [ 'color', settings.color || this.color ],
                [ 'background', settings.bg || this.bg ],
                [ 'fontFamily', settings.font || this.font ]
            ],
            children: [
                ...this.renderWords(parse.words),
                ...this.renderArrows(parse.arcs)
            ]
        }));
    }

    renderWords(words) {
        return (words.map(( { text, tag, lemma, entity, data = [] }, i) => this._el('text', {
            classnames: [ 'displacy-token' ],
            attributes: [
                ['fill', 'currentColor'],
                ['data-tag', tag],
                ['text-anchor', 'middle'],
                ['y', this.offsetY + this.wordSpacing],
                ...data.map(([attr, value]) => (['data-' + attr.replace(' ', '-'), value]))
            ],
            children: [
                this._el('tspan', {
                    classnames: [ 'displacy-word' ],
                    attributes: [
                        ['x', this.offsetX + i * this.distance],
                        ['fill', 'currentColor'],
                        ['data-tag', tag]
                    ],
                    text: text
                }),
                this._el('tspan', {
                    classnames: [ 'displacy-tag' ],
                    attributes: [
                        ['x', this.offsetX + i * this.distance],
                        ['dy', '2em'],
                        ['fill', 'currentColor'],
                        ['data-tag', tag]
                    ],
                    text: tag
                }),
                this._el('tspan', {
                    classnames: [ 'displacy-lemma' ],
                    attributes: [
                        ['x', this.offsetX + i * this.distance],
                        ['dy', '2em'],
                        ['fill', 'currentColor'],
                        ['data-tag', lemma]
                    ],
                    text: lemma
                }),
                this._el('tspan', {
                    classnames: [ 'displacy-entity' ],
                    attributes: [
                        ['x', this.offsetX + i * this.distance],
                        ['dy', '2em'],
                        ['fill', 'currentColor'],
                        ['data-tag', entity]
                    ],
                    text: entity
                })
            ]
        })));
    }

    renderArrows(arcs) {
        return arcs.map(({ label, end, start, dir, data = [] }, i) => {
            const level = this.levels.indexOf(end - start) + 1;
            const startX = this.offsetX + start * this.distance + this.arrowSpacing * (this.highestLevel - level) / 4;
            const startY = this.offsetY;
            const endpoint = this.offsetX + (end - start) * this.distance + start * this.distance - this.arrowSpacing * (this.highestLevel - level) / 4;

            let curve = this.offsetY - level * this.distance / 2;
            if(curve == 0 && this.levels.length > 5) curve = -this.distance;

            return this._el('g', {
                classnames: [ 'displacy-arrow' ],
                attributes: [
                    [ 'data-dir', dir ],
                    [ 'data-label', label ],
                    ...data.map(([attr, value]) => (['data-' + attr.replace(' ', '-'), value]))
                ],
                children:  [
                    this._el('path', {
                        id: 'arrow-' + i,
                        classnames: [ 'displacy-arc' ],
                        attributes: [
                            [ 'd', `M${startX},${startY} C${startX},${curve} ${endpoint},${curve} ${endpoint},${startY}`],
                            [ 'stroke-width', this.arrowStroke + 'px' ],
                            [ 'fill', 'none' ],
                            [ 'stroke', 'currentColor' ],
                            [ 'data-dir', dir ],
                            [ 'data-label', label ]
                        ]
                    }),

                    this._el('text', {
                        attributes: [
                            [ 'dy', '1em' ]
                        ],
                        children: [
                            this._el('textPath', {
                                xlink: '#arrow-' + i,
                                classnames: [ 'displacy-label' ],
                                attributes: [
                                    [ 'startOffset', '50%' ],
                                    [ 'fill', 'currentColor' ],
                                    [ 'text-anchor', 'middle' ],
                                    [ 'data-label', label ],
                                    [ 'data-dir', dir ]
                                ],
                                text: label
                            })
                        ]
                    }),

                    this._el('path', {
                        classnames: [ 'displacy-arrowhead' ],
                        attributes: [
                            [ 'd', `M${(dir == 'left') ? startX : endpoint},${startY + 2} L${(dir == 'left') ? startX - this.arrowWidth + 2 : endpoint + this.arrowWidth - 2},${startY - this.arrowWidth} ${(dir == 'left') ? startX + this.arrowWidth - 2 : endpoint - this.arrowWidth + 2},${startY - this.arrowWidth}` ],
                            [ 'fill', 'currentColor' ],
                            [ 'data-label', label ],
                            [ 'data-dir', dir ]
                        ]
                    })
                ]
            });
        });
    }

    _el(tag, options) {
        const { classnames = [], attributes = [], style = [], children = [], text, id, xlink } = options;
        const ns = 'http://www.w3.org/2000/svg';
        const nsx = 'http://www.w3.org/1999/xlink';
        const el = document.createElementNS(ns, tag);

        classnames.forEach(name => el.classList.add(name));
        attributes.forEach(([attr, value]) => el.setAttribute(attr, value));
        style.forEach(([ prop, value ]) => el.style[prop] = value);
        if(xlink) el.setAttributeNS(nsx, 'xlink:href', xlink);
        if(text) el.appendChild(document.createTextNode(text));
        if(id) el.id = id;
        children.forEach(child => el.appendChild(child));
        return el;
    }
}
