"use strict";
/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
exports.id = "vendor-chunks/@standard-schema";
exports.ids = ["vendor-chunks/@standard-schema"];
exports.modules = {

/***/ "(ssr)/./node_modules/@standard-schema/utils/dist/index.js":
/*!***********************************************************!*\
  !*** ./node_modules/@standard-schema/utils/dist/index.js ***!
  \***********************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   SchemaError: () => (/* binding */ SchemaError),\n/* harmony export */   getDotPath: () => (/* binding */ getDotPath)\n/* harmony export */ });\n// src/getDotPath/getDotPath.ts\nfunction getDotPath(issue) {\n  if (issue.path?.length) {\n    let dotPath = \"\";\n    for (const item of issue.path) {\n      const key = typeof item === \"object\" ? item.key : item;\n      if (typeof key === \"string\" || typeof key === \"number\") {\n        if (dotPath) {\n          dotPath += `.${key}`;\n        } else {\n          dotPath += key;\n        }\n      } else {\n        return null;\n      }\n    }\n    return dotPath;\n  }\n  return null;\n}\n\n// src/SchemaError/SchemaError.ts\nvar SchemaError = class extends Error {\n  /**\n   * The schema issues.\n   */\n  issues;\n  /**\n   * Creates a schema error with useful information.\n   *\n   * @param issues The schema issues.\n   */\n  constructor(issues) {\n    super(issues[0].message);\n    this.name = \"SchemaError\";\n    this.issues = issues;\n  }\n};\n\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHNzcikvLi9ub2RlX21vZHVsZXMvQHN0YW5kYXJkLXNjaGVtYS91dGlscy9kaXN0L2luZGV4LmpzIiwibWFwcGluZ3MiOiI7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBLHlCQUF5QixJQUFJO0FBQzdCLFVBQVU7QUFDVjtBQUNBO0FBQ0EsUUFBUTtBQUNSO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFJRSIsInNvdXJjZXMiOlsid2VicGFjazovL2xtcy1mcm9udGVuZC8uL25vZGVfbW9kdWxlcy9Ac3RhbmRhcmQtc2NoZW1hL3V0aWxzL2Rpc3QvaW5kZXguanM/NTQ4OSJdLCJzb3VyY2VzQ29udGVudCI6WyIvLyBzcmMvZ2V0RG90UGF0aC9nZXREb3RQYXRoLnRzXG5mdW5jdGlvbiBnZXREb3RQYXRoKGlzc3VlKSB7XG4gIGlmIChpc3N1ZS5wYXRoPy5sZW5ndGgpIHtcbiAgICBsZXQgZG90UGF0aCA9IFwiXCI7XG4gICAgZm9yIChjb25zdCBpdGVtIG9mIGlzc3VlLnBhdGgpIHtcbiAgICAgIGNvbnN0IGtleSA9IHR5cGVvZiBpdGVtID09PSBcIm9iamVjdFwiID8gaXRlbS5rZXkgOiBpdGVtO1xuICAgICAgaWYgKHR5cGVvZiBrZXkgPT09IFwic3RyaW5nXCIgfHwgdHlwZW9mIGtleSA9PT0gXCJudW1iZXJcIikge1xuICAgICAgICBpZiAoZG90UGF0aCkge1xuICAgICAgICAgIGRvdFBhdGggKz0gYC4ke2tleX1gO1xuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgIGRvdFBhdGggKz0ga2V5O1xuICAgICAgICB9XG4gICAgICB9IGVsc2Uge1xuICAgICAgICByZXR1cm4gbnVsbDtcbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIGRvdFBhdGg7XG4gIH1cbiAgcmV0dXJuIG51bGw7XG59XG5cbi8vIHNyYy9TY2hlbWFFcnJvci9TY2hlbWFFcnJvci50c1xudmFyIFNjaGVtYUVycm9yID0gY2xhc3MgZXh0ZW5kcyBFcnJvciB7XG4gIC8qKlxuICAgKiBUaGUgc2NoZW1hIGlzc3Vlcy5cbiAgICovXG4gIGlzc3VlcztcbiAgLyoqXG4gICAqIENyZWF0ZXMgYSBzY2hlbWEgZXJyb3Igd2l0aCB1c2VmdWwgaW5mb3JtYXRpb24uXG4gICAqXG4gICAqIEBwYXJhbSBpc3N1ZXMgVGhlIHNjaGVtYSBpc3N1ZXMuXG4gICAqL1xuICBjb25zdHJ1Y3Rvcihpc3N1ZXMpIHtcbiAgICBzdXBlcihpc3N1ZXNbMF0ubWVzc2FnZSk7XG4gICAgdGhpcy5uYW1lID0gXCJTY2hlbWFFcnJvclwiO1xuICAgIHRoaXMuaXNzdWVzID0gaXNzdWVzO1xuICB9XG59O1xuZXhwb3J0IHtcbiAgU2NoZW1hRXJyb3IsXG4gIGdldERvdFBhdGhcbn07XG4iXSwibmFtZXMiOltdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///(ssr)/./node_modules/@standard-schema/utils/dist/index.js\n");

/***/ })

};
;