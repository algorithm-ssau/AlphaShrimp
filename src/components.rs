use leptos::prelude::*;

#[component]
pub fn FormInput(
    label: &'static str,
    name: &'static str,
    #[prop(into)] type_: Signal<String>,
    #[prop(into, optional)] placeholder: String,
    #[prop(optional)] value: Option<RwSignal<String>>,
    #[prop(optional)] children: Option<Children>,
) -> impl IntoView {
    view! {
        <div class="form-group">
            <label class="form-label" for=name>{label}</label>
            <div class="input-wrapper">
                <input class="form-input" id=name name=name type=type_ placeholder=placeholder
                    on:input=move |ev| {
                        if let Some(sig) = value {
                            sig.set(event_target_value(&ev));
                        }
                    }
                />
                {children.map(|c| c())}
            </div>
        </div>
    }
}

#[component]
pub fn FormPasswordButton(
    #[prop(into)] type_: RwSignal<String>,
    #[prop(optional)] children: Option<Children>,
) -> impl IntoView {
    view! {
        <button
            type="button"
            class="toggle-password"
            on:click=move |_| type_.set(if type_.get() == "password" { "text".into() } else { "password".into() })
            aria-label="Показать пароль">
            {children.map(|c| c())}
        </button>
    }
}

#[component]
pub fn EyeSVG() -> impl IntoView {
    view! {
        <svg class="eye-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
            <circle cx="12" cy="12" r="3" />
            <line class="eye-slash" x1="1" y1="1" x2="23" y2="23" style="display:none" />
        </svg>
    }
}

#[component]
pub fn TopHeader(
    #[prop(optional)] back_href: Option<&'static str>,
) -> impl IntoView {
    view! {
        <div class="header">
            <Show when=move || back_href.is_some()>
                <a href=back_href.unwrap_or("#") class="back-btn" aria-label="Назад">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"
                        stroke-linejoin="round">
                        <path d="M19 12H5" />
                        <path d="M12 19l-7-7 7-7" />
                    </svg>
                </a>
            </Show>
            <span class="header-title">Классический кроссворд</span>
        </div>
    }
}

#[component]
pub fn Connector(
    #[prop(optional, default = 40)] width: i32,
    #[prop(optional, default = 18)] offset: i32,
    #[prop(into, optional)] animate: Option<Signal<bool>>,
) -> impl IntoView {
    view! {
        <div class="connector-area" class:no-anim=move || !animate.map(|s| s.get()).unwrap_or(true) style=format!("--conn-width: {}px; left: calc(100% + {}px);", width, offset)>
            <div class="connector-line"></div>
        </div>
    }
}

#[component]
pub fn CrosswordIcon() -> impl IntoView {
    view! {
        <svg class="icon" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3"
            stroke-linecap="round" stroke-linejoin="round">
            <path d="M25 52V40L20 26L15 40V82H25V68M25 60L25 60.1M15 74H25M15 40H25" />
            <path d="M54 20V80M66 20V80M30 32V44M42 32V44M78 32V44M42 56V68M78 56V68M54 20H66M54 80H66M30 32H78M30 44H78M42 56H78M42 68H78" />
        </svg>
    }
}

#[component]
pub fn CrosswordList(
    #[prop(into)] selected: RwSignal<Option<usize>>,
) -> impl IntoView {
    view! {
        <div class="list-box">
            {(1..=3).map(|i| view! {
                <div class="list-item"
                    class:selected=move || selected.get() == Some(i)
                    on:click=move |_| selected.set(Some(i))>
                    <CrosswordIcon />
                    {format!("Кроссворд {}", i)}
                </div>
            }).collect_view()}
        </div>
    }
}

#[component]
pub fn DictionaryList(
    #[prop(into)] selected: RwSignal<Option<usize>>,
) -> impl IntoView {
    view! {
        <div class="list-box">
            {(1..=3).map(|i| view! {
                <div class="list-item"
                    class:selected=move || selected.get() == Some(i)
                    on:click=move |_| selected.set(Some(i))>
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"
                        stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 3H6c-1.1 0-2 0.9-2 2v14c0 1.1 0.9 2 2 2h12c1.1 0 2-0.9 2-2V9L14 3z" />
                        <path d="M14 3v6h6" />
                        <path d="M8 12h8M8 16h8" />
                    </svg>
                    {format!("Словарь {}", i)}
                </div>
            }).collect_view()}
        </div>
    }
}

#[component]
pub fn SettingsTab(
    #[prop(into)] volume: RwSignal<i32>,
    #[prop(into)] sound_on: RwSignal<bool>,
) -> impl IntoView {
    view! {
        <div class="tab-content">
            <h2 class="content-title">Настройки</h2>
            <div class="settings-grid">
                <span class="settings-label">"Громкость:"</span>
                <input type="range" min="0" max="100" prop:value=move || volume.get().to_string()
                    on:input=move |ev| {
                        if let Ok(v) = event_target_value(&ev).parse::<i32>() {
                            volume.set(v);
                        }
                    }
                />
                <span class="volume-value">{move || volume.get()}</span>

                <span class="settings-label">"Звук:"</span>
                <span></span>
                <button class="sound-toggle" class:muted=move || !sound_on.get()
                    style="justify-self:center;"
                    on:click=move |_| sound_on.update(|v| *v = !*v)>
                    <svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor"
                        stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
                        <Show when=move || sound_on.get()>
                            <g>
                                <path d="M15.54 8.46a5 5 0 0 1 0 7.07" fill="none" stroke-width="2" />
                                <path d="M19.07 4.93a10 10 0 0 1 0 14.14" fill="none" stroke-width="2" />
                            </g>
                        </Show>
                        <Show when=move || !sound_on.get()>
                            <g>
                                <line x1="23" y1="9" x2="17" y2="15" stroke-width="2" />
                                <line x1="17" y1="9" x2="23" y2="15" stroke-width="2" />
                            </g>
                        </Show>
                    </svg>
                </button>
            </div>
            <div class="action-row" style="margin-top:24px;">
                <button class="action-btn">
                    Применить
                    <svg style="width:14px;height:14px;vertical-align:middle;margin-left:4px;"
                        viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
                        stroke-linecap="round" stroke-linejoin="round">
                        <path d="M23 4v6h-6" />
                        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
                    </svg>
                </button>
            </div>
        </div>
    }
}
