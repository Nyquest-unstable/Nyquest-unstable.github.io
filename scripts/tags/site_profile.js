'use strict';

function loadProfile() {
  const profile = hexo.locals.get('data').site_profile;

  if (!profile) {
    throw new Error('Missing source/_data/site_profile.yml');
  }

  return profile;
}

function renderContact(profile) {
  return [
    '- GitHub：<' + profile.github_url + '>',
    '- 邮箱：`' + profile.email + '`'
  ].join('\n');
}

function renderAboutContact(profile) {
  return [
    profile.summary_short,
    '',
    renderContact(profile),
    '- 详细介绍与服务方向：[关于我](' + profile.resume_path + ')'
  ].join('\n');
}

hexo.extend.tag.register('site_profile', function(args) {
  const profile = loadProfile();
  const mode = (args[0] || 'contact').trim();

  if (mode === 'contact') {
    return renderContact(profile);
  }

  if (mode === 'about_contact') {
    return renderAboutContact(profile);
  }

  throw new Error('Unsupported site_profile mode: ' + mode);
}, {ends: false});
