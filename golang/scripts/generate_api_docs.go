package main

import (
	"bytes"
	"fmt"
	"go/ast"
	"go/doc"
	"go/parser"
	"go/printer"
	"go/token"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
)

type docMapping struct {
	Target          string
	Title           string
	PackagePath     string
	TypeNames       []string
	FuncNames       []string
	ValueNames      []string
	IncludeAllTypes bool
	IncludeAllFuncs bool
}

type packageDoc struct {
	doc  *doc.Package
	fset *token.FileSet
}

var mappings = []docMapping{
	{
		Target:          "common-features/basics/agentbay.md",
		Title:           "AgentBay",
		PackagePath:     "pkg/agentbay",
		TypeNames:       []string{"AgentBayConfig", "AgentBay", "Option"},
		IncludeAllFuncs: true,
	},
	{
		Target:      "common-features/basics/session.md",
		Title:       "Session",
		PackagePath: "pkg/agentbay",
		TypeNames: []string{
			"SessionResult",
			"SessionListResult",
			"InfoResult",
			"LabelResult",
			"LinkResult",
			"DeleteResult",
			"McpTool",
			"McpToolsResult",
			"SessionInfo",
			"Session",
			"CreateSessionParams",
			"ContextSync",
			"SyncPolicy",
			"UploadPolicy",
			"DownloadPolicy",
			"DeletePolicy",
			"ExtractPolicy",
			"RecyclePolicy",
			"WhiteList",
			"BWList",
		},
		IncludeAllFuncs: true,
	},
	{
		Target:          "common-features/basics/command.md",
		Title:           "Command",
		PackagePath:     "pkg/agentbay/command",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:      "common-features/basics/context.md",
		Title:       "Context",
		PackagePath: "pkg/agentbay",
		TypeNames: []string{
			"Context",
			"ContextResult",
			"ContextListResult",
			"ContextCreateResult",
			"ContextModifyResult",
			"ContextDeleteResult",
			"ContextClearResult",
			"ContextService",
			"ContextListParams",
			"ContextFileUrlResult",
			"ContextFileEntry",
			"ContextFileListResult",
			"ContextFileDeleteResult",
		},
		IncludeAllFuncs: true,
	},
	{
		Target:      "common-features/basics/context-manager.md",
		Title:       "Context Manager",
		PackagePath: "pkg/agentbay",
		TypeNames: []string{
			"ContextStatusData",
			"ContextStatusItem",
			"ContextInfoResult",
			"ContextSyncResult",
			"ContextManager",
		},
		IncludeAllFuncs: true,
	},
	{
		Target:          "common-features/basics/filesystem.md",
		Title:           "File System",
		PackagePath:     "pkg/agentbay/filesystem",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "common-features/basics/logging.md",
		Title:           "Logging",
		PackagePath:     "pkg/agentbay",
		TypeNames:       []string{"LoggerConfig"},
		IncludeAllFuncs: true,
		ValueNames:      []string{"LOG_DEBUG", "LOG_INFO", "LOG_WARN", "LOG_ERROR"},
	},
	{
		Target:          "common-features/advanced/agent.md",
		Title:           "Agent",
		PackagePath:     "pkg/agentbay/agent",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "common-features/advanced/oss.md",
		Title:           "OSS",
		PackagePath:     "pkg/agentbay/oss",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "browser-use/browser.md",
		Title:           "Browser",
		PackagePath:     "pkg/agentbay/browser",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "codespace/code.md",
		Title:           "Code",
		PackagePath:     "pkg/agentbay/code",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "computer-use/application.md",
		Title:           "Application",
		PackagePath:     "pkg/agentbay/application",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "computer-use/computer.md",
		Title:           "Computer",
		PackagePath:     "pkg/agentbay/computer",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "computer-use/ui.md",
		Title:           "UI",
		PackagePath:     "pkg/agentbay/ui",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "computer-use/window.md",
		Title:           "Window",
		PackagePath:     "pkg/agentbay/window",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "mobile-use/mobile.md",
		Title:           "Mobile",
		PackagePath:     "pkg/agentbay/mobile",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
}

var packageCache = map[string]*packageDoc{}

func main() {
	_, currentFile, _, _ := runtime.Caller(0)
	scriptDir := filepath.Dir(currentFile)
	projectRoot := filepath.Dir(scriptDir)
	docsRoot := filepath.Join(projectRoot, "docs", "api-preview", "golang", "latest")

	if err := os.RemoveAll(docsRoot); err != nil {
		panic(err)
	}
	if err := os.MkdirAll(docsRoot, 0o755); err != nil {
		panic(err)
	}

	for _, mapping := range mappings {
		if err := generateDoc(projectRoot, docsRoot, mapping); err != nil {
			panic(err)
		}
	}

	if err := writeReadme(docsRoot); err != nil {
		panic(err)
	}
}

func generateDoc(projectRoot, docsRoot string, mapping docMapping) error {
	pkgDoc, err := loadPackageDoc(projectRoot, mapping.PackagePath)
	if err != nil {
		return err
	}

	var buf bytes.Buffer
	fmt.Fprintf(&buf, "# %s API Reference\n\n", mapping.Title)

	if pkgComment := strings.TrimSpace(pkgDoc.doc.Doc); pkgComment != "" {
		buf.WriteString(pkgComment)
		buf.WriteString("\n\n")
	}

	types, err := selectTypes(pkgDoc.doc, mapping)
	if err != nil {
		return err
	}
	for _, typ := range types {
		writeType(&buf, pkgDoc, typ)
	}

	funcs, err := selectFuncs(pkgDoc.doc, mapping)
	if err != nil {
		return err
	}
	if len(funcs) > 0 {
		buf.WriteString("## Functions\n\n")
		for _, fn := range funcs {
			writeFunc(&buf, pkgDoc, fn)
		}
	}

	values, err := selectValues(pkgDoc.doc, mapping.ValueNames)
	if err != nil {
		return err
	}
	if len(values) > 0 {
		buf.WriteString("## Constants and Variables\n\n")
		for _, val := range values {
			writeValue(&buf, pkgDoc, val)
		}
	}

	buf.WriteString("---\n\n*Documentation generated automatically from Go source code.*\n")

	outputPath := filepath.Join(docsRoot, mapping.Target)
	if err := os.MkdirAll(filepath.Dir(outputPath), 0o755); err != nil {
		return err
	}
	return os.WriteFile(outputPath, buf.Bytes(), 0o644)
}

func loadPackageDoc(projectRoot, relPath string) (*packageDoc, error) {
	if pkg, ok := packageCache[relPath]; ok {
		return pkg, nil
	}

	dir := filepath.Join(projectRoot, relPath)
	fset := token.NewFileSet()
	pkgs, err := parser.ParseDir(fset, dir, nil, parser.ParseComments)
	if err != nil {
		return nil, fmt.Errorf("parse package %s: %w", relPath, err)
	}

	var first *ast.Package
	for _, pkg := range pkgs {
		first = pkg
		break
	}
	if first == nil {
		return nil, fmt.Errorf("no Go package found in %s", relPath)
	}

	docPkg := doc.New(first, "./", doc.AllDecls)
	packageCache[relPath] = &packageDoc{doc: docPkg, fset: fset}
	return packageCache[relPath], nil
}

func selectTypes(docPkg *doc.Package, mapping docMapping) ([]*doc.Type, error) {
	if mapping.IncludeAllTypes {
		return docPkg.Types, nil
	}
	if len(mapping.TypeNames) == 0 {
		return nil, nil
	}

	index := make(map[string]*doc.Type)
	for _, typ := range docPkg.Types {
		index[typ.Name] = typ
	}

	selected := make([]*doc.Type, 0, len(mapping.TypeNames))
	for _, name := range mapping.TypeNames {
		typ, ok := index[name]
		if !ok {
			return nil, fmt.Errorf("type %s not found in package %s", name, mapping.PackagePath)
		}
		selected = append(selected, typ)
	}
	return selected, nil
}

func selectFuncs(docPkg *doc.Package, mapping docMapping) ([]*doc.Func, error) {
	if mapping.IncludeAllFuncs {
		return docPkg.Funcs, nil
	}
	if len(mapping.FuncNames) == 0 {
		return nil, nil
	}

	index := make(map[string]*doc.Func)
	for _, fn := range docPkg.Funcs {
		index[fn.Name] = fn
	}

	selected := make([]*doc.Func, 0, len(mapping.FuncNames))
	for _, name := range mapping.FuncNames {
		fn, ok := index[name]
		if !ok {
			return nil, fmt.Errorf("function %s not found in package %s", name, mapping.PackagePath)
		}
		selected = append(selected, fn)
	}
	return selected, nil
}

func selectValues(docPkg *doc.Package, names []string) ([]*doc.Value, error) {
	if len(names) == 0 {
		return nil, nil
	}

	wanted := make(map[string]bool)
	for _, name := range names {
		wanted[name] = true
	}

	var results []*doc.Value
	seen := make(map[*doc.Value]bool)
	search := append(append([]*doc.Value{}, docPkg.Consts...), docPkg.Vars...)

	for _, value := range search {
		for _, identifier := range value.Names {
			if wanted[identifier] {
				if !seen[value] {
					results = append(results, value)
					seen[value] = true
				}
				delete(wanted, identifier)
			}
		}
	}

	if len(wanted) > 0 {
		missing := make([]string, 0, len(wanted))
		for name := range wanted {
			missing = append(missing, name)
		}
		sort.Strings(missing)
		return nil, fmt.Errorf("constants or variables %v not found in package %s", missing, docPkg.Name)
	}

	return results, nil
}

func writeType(buf *bytes.Buffer, pkg *packageDoc, typ *doc.Type) {
	fmt.Fprintf(buf, "## Type %s\n\n", typ.Name)
	buf.WriteString("```go\n")
	buf.WriteString(formatNode(pkg.fset, typ.Decl))
	buf.WriteString("\n```\n\n")
	if text := formatComment(typ.Doc); text != "" {
		buf.WriteString(text)
		buf.WriteString("\n\n")
	}

	if len(typ.Methods) > 0 {
		buf.WriteString("### Methods\n\n")
		for _, method := range typ.Methods {
			fmt.Fprintf(buf, "#### %s\n\n", method.Name)
			buf.WriteString("```go\n")
			buf.WriteString(formatNode(pkg.fset, method.Decl))
			buf.WriteString("\n```\n\n")
			if text := formatComment(method.Doc); text != "" {
				buf.WriteString(text)
				buf.WriteString("\n\n")
			}
		}
	}

	if len(typ.Funcs) > 0 {
		buf.WriteString("### Related Functions\n\n")
		for _, fn := range typ.Funcs {
			fmt.Fprintf(buf, "#### %s\n\n", fn.Name)
			buf.WriteString("```go\n")
			buf.WriteString(formatNode(pkg.fset, fn.Decl))
			buf.WriteString("\n```\n\n")
			if text := formatComment(fn.Doc); text != "" {
				buf.WriteString(text)
				buf.WriteString("\n\n")
			}
		}
	}
}

func writeFunc(buf *bytes.Buffer, pkg *packageDoc, fn *doc.Func) {
	fmt.Fprintf(buf, "### %s\n\n", fn.Name)
	buf.WriteString("```go\n")
	buf.WriteString(formatNode(pkg.fset, fn.Decl))
	buf.WriteString("\n```\n\n")
	if text := formatComment(fn.Doc); text != "" {
		buf.WriteString(text)
		buf.WriteString("\n\n")
	}
}

func writeValue(buf *bytes.Buffer, pkg *packageDoc, val *doc.Value) {
	title := strings.Join(val.Names, ", ")
	fmt.Fprintf(buf, "### %s\n\n", title)
	buf.WriteString("```go\n")
	buf.WriteString(formatNode(pkg.fset, val.Decl))
	buf.WriteString("\n```\n\n")
	if text := formatComment(val.Doc); text != "" {
		buf.WriteString(text)
		buf.WriteString("\n\n")
	}
}

func formatNode(fset *token.FileSet, node ast.Node) string {
	var buf bytes.Buffer
	if err := printer.Fprint(&buf, fset, node); err != nil {
		return ""
	}
	return buf.String()
}

func formatComment(comment string) string {
	comment = strings.TrimSpace(comment)
	if comment == "" {
		return ""
	}
	var buf bytes.Buffer
	doc.ToText(&buf, comment, "", "\n", 100)
	return strings.TrimSpace(buf.String())
}

func writeReadme(docsRoot string) error {
	sections := map[string][]docMapping{}
	for _, mapping := range mappings {
		section := strings.Split(mapping.Target, "/")[0]
		sections[section] = append(sections[section], mapping)
	}

	keys := make([]string, 0, len(sections))
	for key := range sections {
		keys = append(keys, key)
	}
	sort.Strings(keys)

	var buf bytes.Buffer
	buf.WriteString("# AgentBay Go SDK API Reference\n\n")
	buf.WriteString("This directory is generated. Run `go run scripts/generate_api_docs.go` to refresh it.\n\n")

	for _, key := range keys {
		buf.WriteString(fmt.Sprintf("## %s\n\n", formatSectionTitle(key)))
		for _, mapping := range sections[key] {
			buf.WriteString(fmt.Sprintf("- `%s` – %s\n", mapping.Target, mapping.Title))
		}
		buf.WriteString("\n")
	}

	readmePath := filepath.Join(docsRoot, "README.md")
	return os.WriteFile(readmePath, buf.Bytes(), 0o644)
}

func formatSectionTitle(segment string) string {
	parts := strings.Split(segment, "-")
	for i, part := range parts {
		if part == "" {
			continue
		}
		parts[i] = strings.ToUpper(part[:1]) + strings.ToLower(part[1:])
	}
	return strings.Join(parts, " ")
}
