package agentbay

// UploadStrategy defines the upload strategy for context synchronization
type UploadStrategy string

const (
	// PeriodicUpload uploads files periodically
	PeriodicUpload UploadStrategy = "PERIODIC_UPLOAD"
	// ImmediateUpload uploads files immediately
	ImmediateUpload UploadStrategy = "IMMEDIATE_UPLOAD"
)

// DownloadStrategy defines the download strategy for context synchronization
type DownloadStrategy string

const (
	// DownloadBeforeConnected downloads files before connection
	DownloadBeforeConnected DownloadStrategy = "DOWNLOAD_BEFORE_CONNECTED"
	// DownloadOnDemand downloads files on demand
	DownloadOnDemand DownloadStrategy = "DOWNLOAD_ON_DEMAND"
)

// SyncMode defines the synchronization mode
type SyncMode string

const (
	// SourceFile synchronizes source files
	SourceFile SyncMode = "SOURCE_FILE"
	// FullSync performs full synchronization
	FullSync SyncMode = "FULL_SYNC"
)

// UploadPolicy defines the upload policy for context synchronization
type UploadPolicy struct {
	// AutoUpload enables automatic upload
	AutoUpload bool `json:"auto_upload"`
	// UploadStrategy defines the upload strategy
	UploadStrategy UploadStrategy `json:"upload_strategy"`
	// Period defines the upload period in minutes (for periodic upload)
	Period int `json:"period,omitempty"`
}

// DownloadPolicy defines the download policy for context synchronization
type DownloadPolicy struct {
	// AutoDownload enables automatic download
	AutoDownload bool `json:"auto_download"`
	// DownloadStrategy defines the download strategy
	DownloadStrategy DownloadStrategy `json:"download_strategy"`
}

// DeletePolicy defines the delete policy for context synchronization
type DeletePolicy struct {
	// SyncLocalFile enables synchronization of local file deletions
	SyncLocalFile bool `json:"sync_local_file"`
}

// WhiteList defines the white list configuration
type WhiteList struct {
	// Path is the path to include in the white list
	Path string `json:"path"`
	// ExcludePaths are the paths to exclude from the white list
	ExcludePaths []string `json:"exclude_paths,omitempty"`
}

// BWList defines the black and white list configuration
type BWList struct {
	// WhiteList defines the white list
	WhiteList *WhiteList `json:"white_list,omitempty"`
}

// SyncPolicy defines the synchronization policy
type SyncPolicy struct {
	// UploadPolicy defines the upload policy
	UploadPolicy *UploadPolicy `json:"upload_policy,omitempty"`
	// DownloadPolicy defines the download policy
	DownloadPolicy *DownloadPolicy `json:"download_policy,omitempty"`
	// DeletePolicy defines the delete policy
	DeletePolicy *DeletePolicy `json:"delete_policy,omitempty"`
	// SyncMode defines the synchronization mode
	SyncMode SyncMode `json:"sync_mode"`
	// BWList defines the black and white list
	BWList *BWList `json:"bw_list,omitempty"`
}

// ContextSync defines the context synchronization configuration
type ContextSync struct {
	// ContextID is the ID of the context to synchronize
	ContextID string `json:"context_id"`
	// Path is the path where the context should be mounted
	Path string `json:"path"`
	// Policy defines the synchronization policy
	Policy *SyncPolicy `json:"policy,omitempty"`
}

// NewUploadPolicy creates a new upload policy with default values
func NewUploadPolicy() *UploadPolicy {
	return &UploadPolicy{
		AutoUpload:     true,
		UploadStrategy: PeriodicUpload,
		Period:         15, // Default to 15 minutes
	}
}

// NewDownloadPolicy creates a new download policy with default values
func NewDownloadPolicy() *DownloadPolicy {
	return &DownloadPolicy{
		AutoDownload:     true,
		DownloadStrategy: DownloadBeforeConnected,
	}
}

// NewDeletePolicy creates a new delete policy with default values
func NewDeletePolicy() *DeletePolicy {
	return &DeletePolicy{
		SyncLocalFile: true,
	}
}

// NewSyncPolicy creates a new sync policy with default values
func NewSyncPolicy() *SyncPolicy {
	return &SyncPolicy{
		UploadPolicy:   NewUploadPolicy(),
		DownloadPolicy: NewDownloadPolicy(),
		DeletePolicy:   NewDeletePolicy(),
		SyncMode:       SourceFile,
	}
}

// NewContextSync creates a new context sync configuration
func NewContextSync(contextID, path string) *ContextSync {
	return &ContextSync{
		ContextID: contextID,
		Path:      path,
		Policy:    NewSyncPolicy(),
	}
}

// NewBasicContextSync creates a basic context sync configuration without policies
func NewBasicContextSync(contextID, path string) *ContextSync {
	return &ContextSync{
		ContextID: contextID,
		Path:      path,
	}
}

// WithUploadPolicy sets the upload policy
func (cs *ContextSync) WithUploadPolicy(policy *UploadPolicy) *ContextSync {
	if cs.Policy == nil {
		cs.Policy = NewSyncPolicy()
	}
	cs.Policy.UploadPolicy = policy
	return cs
}

// WithDownloadPolicy sets the download policy
func (cs *ContextSync) WithDownloadPolicy(policy *DownloadPolicy) *ContextSync {
	if cs.Policy == nil {
		cs.Policy = NewSyncPolicy()
	}
	cs.Policy.DownloadPolicy = policy
	return cs
}

// WithDeletePolicy sets the delete policy
func (cs *ContextSync) WithDeletePolicy(policy *DeletePolicy) *ContextSync {
	if cs.Policy == nil {
		cs.Policy = NewSyncPolicy()
	}
	cs.Policy.DeletePolicy = policy
	return cs
}

// WithSyncMode sets the sync mode
func (cs *ContextSync) WithSyncMode(mode SyncMode) *ContextSync {
	if cs.Policy == nil {
		cs.Policy = NewSyncPolicy()
	}
	cs.Policy.SyncMode = mode
	return cs
}

// WithBWList sets the black and white list
func (cs *ContextSync) WithBWList(bwList *BWList) *ContextSync {
	if cs.Policy == nil {
		cs.Policy = NewSyncPolicy()
	}
	cs.Policy.BWList = bwList
	return cs
}

// WithWhiteList sets the white list
func (cs *ContextSync) WithWhiteList(path string, excludePaths []string) *ContextSync {
	whiteList := &WhiteList{
		Path:         path,
		ExcludePaths: excludePaths,
	}
	bwList := &BWList{
		WhiteList: whiteList,
	}
	return cs.WithBWList(bwList)
}
